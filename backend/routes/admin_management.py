from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from models import DashboardStats, MessageResponse
from middleware import get_current_admin_user, log_audit
from database import get_db
from typing import Dict, Optional, List
from datetime import datetime, timezone

router = APIRouter(prefix="/admin", tags=["Admin Management"])

# ============ DASHBOARD & ANALYTICS ============

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """
    Get dashboard statistics for admin panel
    """
    # Count users
    total_users = await db.users.count_documents({})
    
    # Count documents
    total_documents = await db.documents.count_documents({})
    
    # Count transactions
    total_transactions = await db.transactions.count_documents({})
    
    # Count pending requests
    pending_deposits = await db.deposit_requests.count_documents({"status": "pending"})
    pending_withdrawals = await db.withdrawal_requests.count_documents({"status": "pending"})
    pending_kyc = await db.kyc_submissions.count_documents({"status": "pending"})
    
    # Calculate total revenue
    revenue_pipeline = [
        {"$match": {"status": "completed", "type": "purchase"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    revenue_result = await db.transactions.aggregate(revenue_pipeline).to_list(1)
    total_revenue = revenue_result[0]['total'] if revenue_result else 0.0
    
    # Count active stakings
    active_stakings = await db.staking_positions.count_documents({"status": "active"})
    
    # Count active investments
    active_investments = await db.investment_positions.count_documents({"status": "active"})
    
    return DashboardStats(
        total_users=total_users,
        total_documents=total_documents,
        total_transactions=total_transactions,
        pending_deposits=pending_deposits,
        pending_withdrawals=pending_withdrawals,
        pending_kyc=pending_kyc,
        total_revenue=total_revenue,
        active_stakings=active_stakings,
        active_investments=active_investments
    )

# ============ USER MANAGEMENT ============

@router.get("/users")
async def get_all_users(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    kyc_status: Optional[str] = None,
    role: Optional[str] = None
):
    """Get all users with filtering and pagination"""
    skip = (page - 1) * limit
    
    # Build query
    query = {}
    if search:
        query["$or"] = [
            {"email": {"$regex": search, "$options": "i"}},
            {"username": {"$regex": search, "$options": "i"}},
            {"full_name": {"$regex": search, "$options": "i"}}
        ]
    if kyc_status:
        query["kyc_status"] = kyc_status
    if role:
        query["role"] = role
    
    # Get total count
    total = await db.users.count_documents(query)
    
    # Get users
    users = await db.users.find(
        query,
        {"_id": 0, "password_hash": 0, "totp_secret": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: str,
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Get detailed user information"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0, "totp_secret": 0})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get wallet info
    wallet = await db.wallets.find_one({"user_id": user_id}, {"_id": 0})
    
    # Get transaction count
    transaction_count = await db.transactions.count_documents({"user_id": user_id})
    
    # Get staking positions
    staking_positions = await db.staking_positions.find(
        {"user_id": user_id, "status": "active"},
        {"_id": 0}
    ).to_list(100)
    
    # Get investment positions
    investment_positions = await db.investment_positions.find(
        {"user_id": user_id, "status": "active"},
        {"_id": 0}
    ).to_list(100)
    
    return {
        "user": user,
        "wallet": wallet,
        "transaction_count": transaction_count,
        "staking_positions": staking_positions,
        "investment_positions": investment_positions
    }

@router.put("/users/{user_id}/status", response_model=MessageResponse)
async def update_user_status(
    user_id: str,
    is_active: bool,
    current_admin: Dict = Depends(get_current_admin_user),
    request: Request = None,
    db = Depends(get_db)
):
    """Activate or deactivate user"""
    user = await db.users.find_one({"id": user_id})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"is_active": is_active, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    await log_audit(
        db, current_admin['id'], "user_status_updated",
        {"user_id": user_id, "is_active": is_active},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message=f"User {'activated' if is_active else 'deactivated'} successfully")


@router.put("/users/{user_id}/verification", response_model=MessageResponse)
async def toggle_user_verification(
    user_id: str,
    is_verified: bool,
    current_admin: Dict = Depends(get_current_admin_user),
    request: Request = None,
    db = Depends(get_db)
):
    """Toggle user verification badge (blue checkmark)"""
    user = await db.users.find_one({"id": user_id})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"is_verified": is_verified, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    await log_audit(
        db, current_admin['id'], "user_verification_updated",
        {"user_id": user_id, "is_verified": is_verified},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message=f"User verification {'enabled' if is_verified else 'disabled'} successfully")

@router.post("/users/create", response_model=MessageResponse)
async def create_user_by_admin(
    user_data: Dict,
    current_admin: Dict = Depends(get_current_admin_user),
    request: Request = None,
    db = Depends(get_db)
):
    """Admin creates a new user"""
    from security import hash_password
    from models import User
    
    # Check if email already exists
    existing_email = await db.users.find_one({"email": user_data['email']})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = await db.users.find_one({"username": user_data['username']})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    user_dict = {
        "email": user_data['email'],
        "username": user_data['username'],
        "password_hash": hash_password(user_data['password']),
        "full_name": user_data.get('full_name', ''),
        "is_verified": user_data.get('is_verified', False),
        "is_active": user_data.get('is_active', True)
    }
    
    user = User(**user_dict)
    user_doc = user.model_dump()
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    user_doc['updated_at'] = user_doc['updated_at'].isoformat()
    
    await db.users.insert_one(user_doc)
    
    # Create wallet for user
    wallet_doc = {
        "user_id": user.id,
        "balance": 0.0,
        "locked_balance": 0.0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.wallets.insert_one(wallet_doc)
    
    await log_audit(
        db, current_admin['id'], "user_created_by_admin",
        {"new_user_id": user.id, "email": user.email, "username": user.username},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message="User created successfully")

@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str,
    current_admin: Dict = Depends(get_current_admin_user),
    request: Request = None,
    db = Depends(get_db)
):
    """Delete a user"""
    user = await db.users.find_one({"id": user_id})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete user and related data
    await db.users.delete_one({"id": user_id})
    await db.wallets.delete_one({"user_id": user_id})
    await db.transactions.delete_many({"user_id": user_id})
    await db.kyc_submissions.delete_many({"user_id": user_id})
    
    await log_audit(
        db, current_admin['id'], "user_deleted",
        {"user_id": user_id, "email": user.get('email'), "username": user.get('username')},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message="User deleted successfully")

# ============ KYC MANAGEMENT ============

@router.get("/kyc/pending")
async def get_pending_kyc(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get pending KYC submissions"""
    skip = (page - 1) * limit
    
    query = {"status": "pending"}
    total = await db.kyc_submissions.count_documents(query)
    
    kyc_submissions = await db.kyc_submissions.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Enrich with user data
    for submission in kyc_submissions:
        user = await db.users.find_one(
            {"id": submission['user_id']},
            {"_id": 0, "email": 1, "username": 1, "full_name": 1}
        )
        submission['user'] = user
    
    return {
        "submissions": kyc_submissions,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@router.put("/kyc/{kyc_id}/verify", response_model=MessageResponse)
async def verify_kyc(
    kyc_id: str,
    approved: bool,
    admin_note: Optional[str] = None,
    current_admin: Dict = Depends(get_current_admin_user),
    request: Request = None,
    db = Depends(get_db)
):
    """Approve or reject KYC submission"""
    kyc = await db.kyc_submissions.find_one({"id": kyc_id})
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC submission not found"
        )
    
    new_status = "approved" if approved else "rejected"
    
    # Update KYC submission
    await db.kyc_submissions.update_one(
        {"id": kyc_id},
        {"$set": {
            "status": new_status,
            "admin_note": admin_note,
            "reviewed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Update user KYC status
    await db.users.update_one(
        {"id": kyc['user_id']},
        {"$set": {
            "kyc_status": "verified" if approved else "rejected",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    await log_audit(
        db, current_admin['id'], "kyc_verified",
        {"kyc_id": kyc_id, "user_id": kyc['user_id'], "approved": approved, "note": admin_note},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message=f"KYC {'approved' if approved else 'rejected'} successfully")

# ============ DOCUMENT MANAGEMENT ============

@router.get("/documents")
async def get_all_documents(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all documents with filtering"""
    skip = (page - 1) * limit
    
    query = {}
    if status_filter:
        query["status"] = status_filter
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"category": {"$regex": search, "$options": "i"}}
        ]
    
    total = await db.documents.count_documents(query)
    
    documents = await db.documents.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Enrich with seller data
    for doc in documents:
        seller = await db.users.find_one(
            {"id": doc['seller_id']},
            {"_id": 0, "email": 1, "username": 1}
        )
        doc['seller'] = seller
    
    return {
        "documents": documents,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@router.put("/documents/{doc_id}/approve", response_model=MessageResponse)
async def approve_document(
    doc_id: str,
    approved: bool,
    admin_note: Optional[str] = None,
    current_admin: Dict = Depends(get_current_admin_user),
    request: Request = None,
    db = Depends(get_db)
):
    """Approve or reject document"""
    document = await db.documents.find_one({"id": doc_id})
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    new_status = "approved" if approved else "rejected"
    
    await db.documents.update_one(
        {"id": doc_id},
        {"$set": {
            "status": new_status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    await log_audit(
        db, current_admin['id'], "document_status_updated",
        {"document_id": doc_id, "approved": approved, "note": admin_note},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message=f"Document {'approved' if approved else 'rejected'} successfully")

# ============ DEPOSIT MANAGEMENT ============

@router.get("/deposits")
async def get_deposit_requests(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None
):
    """Get deposit requests"""
    skip = (page - 1) * limit
    
    query = {}
    if status_filter:
        query["status"] = status_filter
    
    total = await db.deposit_requests.count_documents(query)
    
    deposits = await db.deposit_requests.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Enrich with user data
    for deposit in deposits:
        user = await db.users.find_one(
            {"id": deposit['user_id']},
            {"_id": 0, "email": 1, "username": 1}
        )
        deposit['user'] = user
    
    return {
        "deposits": deposits,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@router.put("/deposits/{deposit_id}/process", response_model=MessageResponse)
async def process_deposit(
    deposit_id: str,
    approved: bool,
    admin_note: Optional[str] = None,
    current_admin: Dict = Depends(get_current_admin_user),
    request: Request = None,
    db = Depends(get_db)
):
    """Process deposit request"""
    deposit = await db.deposit_requests.find_one({"id": deposit_id})
    
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit request not found"
        )
    
    if deposit['status'] != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deposit already processed"
        )
    
    new_status = "approved" if approved else "rejected"
    
    # Update deposit request
    await db.deposit_requests.update_one(
        {"id": deposit_id},
        {"$set": {
            "status": new_status,
            "admin_note": admin_note,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if approved:
        # Update wallet balance
        await db.wallets.update_one(
            {"user_id": deposit['user_id']},
            {
                "$inc": {"balance": deposit['amount']},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        # Create transaction record
        transaction = {
            "id": f"tx-{deposit_id}",
            "user_id": deposit['user_id'],
            "type": "deposit",
            "amount": deposit['amount'],
            "status": "completed",
            "metadata": {"deposit_id": deposit_id, "approved_by": current_admin['id']},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.transactions.insert_one(transaction)
    
    await log_audit(
        db, current_admin['id'], "deposit_processed",
        {"deposit_id": deposit_id, "user_id": deposit['user_id'], "approved": approved, "amount": deposit['amount']},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message=f"Deposit {'approved' if approved else 'rejected'} successfully")

# ============ WITHDRAWAL MANAGEMENT ============

@router.get("/withdrawals")
async def get_withdrawal_requests(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None
):
    """Get withdrawal requests"""
    skip = (page - 1) * limit
    
    query = {}
    if status_filter:
        query["status"] = status_filter
    
    total = await db.withdrawal_requests.count_documents(query)
    
    withdrawals = await db.withdrawal_requests.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Enrich with user data
    for withdrawal in withdrawals:
        user = await db.users.find_one(
            {"id": withdrawal['user_id']},
            {"_id": 0, "email": 1, "username": 1}
        )
        withdrawal['user'] = user
    
    return {
        "withdrawals": withdrawals,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@router.put("/withdrawals/{withdrawal_id}/process", response_model=MessageResponse)
async def process_withdrawal(
    withdrawal_id: str,
    approved: bool,
    admin_note: Optional[str] = None,
    current_admin: Dict = Depends(get_current_admin_user),
    request: Request = None,
    db = Depends(get_db)
):
    """Process withdrawal request"""
    withdrawal = await db.withdrawal_requests.find_one({"id": withdrawal_id})
    
    if not withdrawal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Withdrawal request not found"
        )
    
    if withdrawal['status'] != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Withdrawal already processed"
        )
    
    new_status = "approved" if approved else "rejected"
    
    # Update withdrawal request
    await db.withdrawal_requests.update_one(
        {"id": withdrawal_id},
        {"$set": {
            "status": new_status,
            "admin_note": admin_note,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if approved:
        # Deduct from wallet
        wallet = await db.wallets.find_one({"user_id": withdrawal['user_id']})
        
        if not wallet or wallet['balance'] < withdrawal['amount']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )
        
        await db.wallets.update_one(
            {"user_id": withdrawal['user_id']},
            {
                "$inc": {"balance": -withdrawal['amount']},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        # Create transaction record
        transaction = {
            "id": f"tx-{withdrawal_id}",
            "user_id": withdrawal['user_id'],
            "type": "withdrawal",
            "amount": withdrawal['amount'],
            "status": "completed",
            "metadata": {"withdrawal_id": withdrawal_id, "approved_by": current_admin['id']},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.transactions.insert_one(transaction)
    
    await log_audit(
        db, current_admin['id'], "withdrawal_processed",
        {"withdrawal_id": withdrawal_id, "user_id": withdrawal['user_id'], "approved": approved, "amount": withdrawal['amount']},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message=f"Withdrawal {'approved' if approved else 'rejected'} successfully")

# ============ TRANSACTIONS ============

@router.get("/transactions")
async def get_all_transactions(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    type_filter: Optional[str] = None,
    status_filter: Optional[str] = None
):
    """Get all transactions"""
    skip = (page - 1) * limit
    
    query = {}
    if type_filter:
        query["type"] = type_filter
    if status_filter:
        query["status"] = status_filter
    
    total = await db.transactions.count_documents(query)
    
    transactions = await db.transactions.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    return {
        "transactions": transactions,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

# ============ AUDIT LOGS ============

@router.get("/audit-logs")
async def get_audit_logs(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    action_filter: Optional[str] = None
):
    """Get audit logs"""
    skip = (page - 1) * limit
    
    query = {}
    if action_filter:
        query["action"] = {"$regex": action_filter, "$options": "i"}
    
    total = await db.audit_logs.count_documents(query)
    
    logs = await db.audit_logs.find(
        query,
        {"_id": 0}
    ).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
    
    return {
        "logs": logs,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }
