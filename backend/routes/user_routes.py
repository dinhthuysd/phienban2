from fastapi import APIRouter, HTTPException, status, Depends, Request, UploadFile, File
from models import MessageResponse, KYCSubmission
from middleware import get_current_user, log_audit
from database import get_db
from typing import Dict, List
from datetime import datetime, timezone
import uuid
import os
from pathlib import Path
import sys

# Add utils to path
sys.path.append('/app/backend')
from utils.kyc_analyzer import KYCDocumentAnalyzer

router = APIRouter(prefix="/user", tags=["User Operations"])

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("/app/backend/uploads/kyc")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/kyc/submit", response_model=MessageResponse)
async def submit_kyc(
    id_type: str,
    files: List[UploadFile] = File(...),
    current_user: Dict = Depends(get_current_user),
    request: Request = None,
    db = Depends(get_db)
):
    """
    Submit KYC documents for verification
    """
    # Check if user already has pending or approved KYC
    existing_kyc = await db.kyc_submissions.find_one({
        "user_id": current_user['id'],
        "status": {"$in": ["pending", "approved"]}
    })
    
    if existing_kyc:
        if existing_kyc['status'] == 'approved':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your KYC is already approved"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a pending KYC submission"
            )
    
    # Validate file types
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf'}
    file_ids = []
    file_paths = []
    
    try:
        # Save files
        for file in files:
            # Check file extension
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid file type: {file.filename}. Only JPG, PNG, and PDF are allowed"
                )
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"{file_id}{file_ext}"
            file_path = UPLOAD_DIR / filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            file_ids.append(file_id)
            file_paths.append(str(file_path))
    
    except Exception as e:
        # Clean up any uploaded files if error occurs
        for file_id in file_ids:
            for ext in allowed_extensions:
                file_path = UPLOAD_DIR / f"{file_id}{ext}"
                if file_path.exists():
                    file_path.unlink()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading files: {str(e)}"
        )
    
    # ===== TỰ ĐỘNG PHÂN TÍCH DOCUMENTS =====
    analysis_results = []
    overall_validation_score = 0
    
    for i, file_path in enumerate(file_paths):
        # Skip PDF files for now (image analysis only)
        if not file_path.lower().endswith('.pdf'):
            try:
                # Analyze document
                validation_result = KYCDocumentAnalyzer.validate_document(file_path, id_type)
                analysis_results.append({
                    'file_id': file_ids[i],
                    'analysis': validation_result
                })
                overall_validation_score += validation_result.get('validation_score', 0)
            except Exception as e:
                analysis_results.append({
                    'file_id': file_ids[i],
                    'analysis': {'error': str(e), 'validation_score': 0}
                })
    
    # Calculate average validation score
    if analysis_results:
        overall_validation_score = overall_validation_score / len(analysis_results)
    
    # Determine auto-approval
    auto_approved = overall_validation_score >= 80
    requires_review = overall_validation_score < 80
    
    # Create KYC submission with analysis
    kyc_submission = KYCSubmission(
        user_id=current_user['id'],
        id_type=id_type,
        file_ids=file_ids
    )
    
    kyc_doc = kyc_submission.model_dump()
    kyc_doc['created_at'] = kyc_doc['created_at'].isoformat()
    
    # Add analysis results
    kyc_doc['analysis'] = {
        'validation_score': round(overall_validation_score, 2),
        'auto_approved': auto_approved,
        'requires_manual_review': requires_review,
        'file_analyses': analysis_results,
        'analyzed_at': datetime.now(timezone.utc).isoformat()
    }
    
    # Set initial status based on analysis
    if auto_approved:
        kyc_doc['status'] = 'approved'
        kyc_doc['reviewed_at'] = datetime.now(timezone.utc).isoformat()
        kyc_doc['admin_note'] = 'Automatically approved based on quality analysis'
    
    await db.kyc_submissions.insert_one(kyc_doc)
    
    # Update user KYC status
    new_kyc_status = 'verified' if auto_approved else 'pending'
    await db.users.update_one(
        {"id": current_user['id']},
        {"$set": {"kyc_status": new_kyc_status}}
    )
    
    # Log audit
    await log_audit(
        db, current_user['id'], "kyc_submitted",
        {
            "kyc_id": kyc_submission.id, 
            "id_type": id_type, 
            "files_count": len(file_ids),
            "validation_score": round(overall_validation_score, 2),
            "auto_approved": auto_approved
        },
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    # Return appropriate message
    if auto_approved:
        return MessageResponse(
            message="KYC documents submitted and automatically approved! Your account is now verified.",
            success=True
        )
    else:
        return MessageResponse(
            message="KYC documents submitted successfully. Please wait for admin review.",
            success=True
        )

@router.get("/kyc/status")
async def get_kyc_status(
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get user's KYC submission status
    """
    kyc = await db.kyc_submissions.find_one(
        {"user_id": current_user['id']},
        {"_id": 0}
    )
    
    if not kyc:
        return {
            "status": "not_submitted",
            "message": "You haven't submitted KYC documents yet"
        }
    
    return {
        "status": kyc['status'],
        "id_type": kyc.get('id_type'),
        "submitted_at": kyc.get('created_at'),
        "reviewed_at": kyc.get('reviewed_at'),
        "admin_note": kyc.get('admin_note')
    }

@router.get("/profile")
async def get_user_profile(
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get current user profile"""
    user = await db.users.find_one(
        {"id": current_user['id']},
        {"_id": 0, "password_hash": 0, "totp_secret": 0}
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/auth/google")
async def google_auth(
    token: str,
    request: Request,
    db = Depends(get_db)
):
    """
    Google OAuth authentication for users
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        import os
        
        # Verify the Google token
        GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
        
        if not GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth not configured"
            )
        
        # Verify token
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Get user info from Google
        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name', '')
        
        # Check if user exists
        user = await db.users.find_one({"google_id": google_id})
        
        if not user:
            # Check if email already exists with different auth method
            user = await db.users.find_one({"email": email})
            
            if user:
                # Link Google account to existing user
                await db.users.update_one(
                    {"id": user['id']},
                    {"$set": {"google_id": google_id, "updated_at": datetime.now(timezone.utc).isoformat()}}
                )
            else:
                # Create new user
                from models import User
                from security import hash_password
                import secrets
                
                # Generate random username from email
                username = email.split('@')[0] + '_' + secrets.token_hex(4)
                
                user_dict = {
                    "email": email,
                    "username": username,
                    "password_hash": hash_password(secrets.token_hex(16)),  # Random password
                    "full_name": name,
                    "google_id": google_id,
                    "is_verified": False,
                    "is_active": True
                }
                
                user = User(**user_dict)
                user_doc = user.model_dump()
                user_doc['created_at'] = user_doc['created_at'].isoformat()
                user_doc['updated_at'] = user_doc['updated_at'].isoformat()
                
                await db.users.insert_one(user_doc)
                
                # Create wallet
                wallet_doc = {
                    "user_id": user.id,
                    "balance": 0.0,
                    "locked_balance": 0.0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                await db.wallets.insert_one(wallet_doc)
                
                user = user_doc
        
        # Create JWT tokens
        from security import create_access_token, create_refresh_token
        
        token_data = {
            "sub": user['id'],
            "email": user['email'],
            "role": user.get('role', 'user')
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Log audit
        await log_audit(
            db, user['id'], "user_login_google",
            {"email": user['email']},
            request.client.host if request else None,
            request.headers.get("user-agent") if request else None
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "username": user['username'],
                "full_name": user.get('full_name'),
                "is_verified": user.get('is_verified', False)
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )
