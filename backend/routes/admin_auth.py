from fastapi import APIRouter, HTTPException, status, Depends, Request
from models import AdminUserCreate, AdminLogin, TokenResponse, MessageResponse, AdminUser, AdminUpdateProfile, AdminChangePassword
from security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, generate_totp_secret, verify_totp, generate_qr_uri
from middleware import log_audit, get_current_admin_user
from database import get_db
from datetime import datetime, timezone, timedelta
from typing import Dict
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/auth", tags=["Admin Authentication"])

@router.post("/login", response_model=TokenResponse)
async def admin_login(login_data: AdminLogin, request: Request, db = Depends(get_db)):
    """
    Admin login endpoint
    - Validates credentials
    - Checks 2FA if enabled
    - Returns JWT tokens
    """
    try:
        # Find admin user by email OR username
        admin_user = await db.admin_users.find_one({
            "$or": [
                {"email": login_data.email},
                {"username": login_data.email}  # Allow login with username too
            ]
        })
        
        if not admin_user:
            await log_audit(
                db, None, "admin_login_failed",
                {"email": login_data.email, "reason": "user_not_found"},
                request.client.host,
                request.headers.get("user-agent")
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, admin_user['password_hash']):
            await log_audit(
                db, admin_user['id'], "admin_login_failed",
                {"reason": "invalid_password"},
                request.client.host,
                request.headers.get("user-agent")
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if admin is active
        if not admin_user.get('is_active', True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is deactivated"
            )
        
        # Check 2FA if enabled
        if admin_user.get('is_2fa_enabled') and admin_user.get('totp_secret'):
            if not login_data.totp_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="2FA code required"
                )
            
            if not verify_totp(admin_user['totp_secret'], login_data.totp_code):
                await log_audit(
                    db, admin_user['id'], "admin_login_failed",
                    {"reason": "invalid_2fa_code"},
                    request.client.host,
                    request.headers.get("user-agent")
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid 2FA code"
                )
        
        # FIX: Update last_login - sử dụng None thay vì datetime để tránh lỗi validation
        try:
            await db.admin_users.update_one(
                {"id": admin_user['id']},
                {"$set": {"last_login": None}}  # Sử dụng None thay vì datetime
            )
        except Exception as e:
            logger.warning(f"Could not update last_login: {str(e)}")
            # Continue even if last_login update fails
        
        # Create tokens
        token_data = {
            "sub": admin_user['id'],
            "email": admin_user['email'],
            "role": admin_user['role']
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Log successful login
        await log_audit(
            db, admin_user['id'], "admin_login_success",
            {"email": admin_user['email'], "role": admin_user['role']},
            request.client.host,
            request.headers.get("user-agent")
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/register", response_model=MessageResponse)
async def register_admin(
    admin_data: AdminUserCreate,
    request: Request,
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """
    Register new admin user (Only super_admin can create admins)
    """
    try:
        # Only super_admin can create new admins
        if current_admin['role'] != 'super_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admin can create new admins"
            )
        
        # Check if email already exists
        existing_email = await db.admin_users.find_one({"email": admin_data.email})
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_username = await db.admin_users.find_one({"username": admin_data.username})
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create admin user
        admin_dict = admin_data.model_dump()
        admin_dict['password_hash'] = hash_password(admin_dict.pop('password'))
        
        admin_user = AdminUser(**admin_dict)
        admin_doc = admin_user.model_dump()
        admin_doc['created_at'] = admin_doc['created_at'].isoformat()
        admin_doc['updated_at'] = admin_doc['updated_at'].isoformat()
        
        await db.admin_users.insert_one(admin_doc)
        
        # Log audit
        await log_audit(
            db, current_admin['id'], "admin_user_created",
            {"new_admin_id": admin_user.id, "email": admin_user.email, "role": admin_user.role},
            request.client.host,
            request.headers.get("user-agent")
        )
        
        return MessageResponse(message="Admin user created successfully")
        
    except Exception as e:
        logger.error(f"Register admin error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/profile")
async def get_admin_profile(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Get current admin profile"""
    try:
        admin = await db.admin_users.find_one(
            {"id": current_admin['id']}, 
            {"_id": 0, "password_hash": 0, "totp_secret": 0}
        )
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        
        return admin
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/profile", response_model=MessageResponse)
async def update_admin_profile(
    profile_data: AdminUpdateProfile,
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Update admin profile"""
    try:
        update_data = {k: v for k, v in profile_data.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data to update"
            )
        
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        await db.admin_users.update_one(
            {"id": current_admin['id']},
            {"$set": update_data}
        )
        
        return MessageResponse(message="Profile updated successfully")
        
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/change-password", response_model=MessageResponse)
async def change_admin_password(
    password_data: AdminChangePassword,
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Change admin password"""
    try:
        admin = await db.admin_users.find_one({"id": current_admin['id']})
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        
        # Verify old password
        if not verify_password(password_data.old_password, admin['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid old password"
            )
        
        # Update password
        new_password_hash = hash_password(password_data.new_password)
        
        await db.admin_users.update_one(
            {"id": current_admin['id']},
            {"$set": {
                "password_hash": new_password_hash,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return MessageResponse(message="Password changed successfully")
        
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/2fa/setup")
async def setup_2fa(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Setup 2FA for admin"""
    try:
        # Generate TOTP secret
        secret = generate_totp_secret()
        qr_uri = generate_qr_uri(secret, current_admin['email'], "Trading Admin")
        
        # Save secret (but don't enable 2FA yet)
        await db.admin_users.update_one(
            {"id": current_admin['id']},
            {"$set": {"totp_secret": secret}}
        )
        
        return {
            "secret": secret,
            "qr_uri": qr_uri,
            "message": "Scan QR code with Google Authenticator and verify with a code"
        }
        
    except Exception as e:
        logger.error(f"2FA setup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/2fa/verify", response_model=MessageResponse)
async def verify_and_enable_2fa(
    totp_code: str,
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Verify and enable 2FA"""
    try:
        admin = await db.admin_users.find_one({"id": current_admin['id']})
        
        if not admin or not admin.get('totp_secret'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA setup not initiated"
            )
        
        # Verify code
        if not verify_totp(admin['totp_secret'], totp_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 2FA code"
            )
        
        # Enable 2FA
        await db.admin_users.update_one(
            {"id": current_admin['id']},
            {"$set": {"is_2fa_enabled": True}}
        )
        
        return MessageResponse(message="2FA enabled successfully")
        
    except Exception as e:
        logger.error(f"2FA verify error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/2fa/disable", response_model=MessageResponse)
async def disable_2fa(
    password: str,
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Disable 2FA (requires password confirmation)"""
    try:
        admin = await db.admin_users.find_one({"id": current_admin['id']})
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        
        # Verify password
        if not verify_password(password, admin['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
        
        # Disable 2FA
        await db.admin_users.update_one(
            {"id": current_admin['id']},
            {"$set": {"is_2fa_enabled": False, "totp_secret": None}}
        )
        
        return MessageResponse(message="2FA disabled successfully")
        
    except Exception as e:
        logger.error(f"2FA disable error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout", response_model=MessageResponse)
async def admin_logout(
    request: Request,
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Admin logout"""
    try:
        await log_audit(
            db, current_admin['id'], "admin_logout",
            {},
            request.client.host,
            request.headers.get("user-agent")
        )
        
        return MessageResponse(message="Logged out successfully")
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )