from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from models import (
    APIToken, APITokenCreate, APITokenUpdate,
    APIPermission, APIPermissionCreate, APIPermissionUpdate,
    SystemSettings, SystemSettingsUpdate,
    AdminUserCreate, MessageResponse
)
from middleware import get_current_admin_user, get_current_super_admin, log_audit
from database import get_db
from security import hash_password, generate_secure_token
from typing import Dict, Optional, List
from datetime import datetime, timezone, timedelta
import hashlib

router = APIRouter(prefix="/admin", tags=["Admin Advanced Features"])

# ============ API TOKEN MANAGEMENT ============

@router.post("/api-tokens", response_model=Dict)
async def create_api_token(
    token_data: APITokenCreate,
    current_admin: Dict = Depends(get_current_admin_user),
    request: Request = None,
    db = Depends(get_db)
):
    """
    Create API token for a user
    Only admins can create API tokens
    """
    # Verify user exists
    user = await db.users.find_one({"id": token_data.user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate unique API key
    api_key = f"tk_{generate_secure_token(32)}"
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Calculate expiration
    expires_at = None
    if token_data.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=token_data.expires_in_days)
    
    # Create token
    token = APIToken(
        user_id=token_data.user_id,
        name=token_data.name,
        token_key=api_key_hash,
        permissions=token_data.permissions,
        expires_at=expires_at
    )
    
    token_doc = token.model_dump()
    token_doc['created_at'] = token_doc['created_at'].isoformat()
    token_doc['updated_at'] = token_doc['updated_at'].isoformat()
    if token_doc['expires_at']:
        token_doc['expires_at'] = token_doc['expires_at'].isoformat()
    
    await db.api_tokens.insert_one(token_doc)
    
    # Log audit
    await log_audit(
        db, current_admin['id'], "api_token_created",
        {"token_id": token.id, "user_id": token_data.user_id, "name": token_data.name},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    # Return token with plain API key (only shown once)
    return {
        "message": "API token created successfully",
        "token_id": token.id,
        "api_key": api_key,  # Only returned once!
        "name": token.name,
        "permissions": token.permissions,
        "expires_at": token.expires_at.isoformat() if token.expires_at else None
    }

@router.get("/api-tokens")
async def get_all_api_tokens(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """Get all API tokens with filtering"""
    skip = (page - 1) * limit
    
    query = {}
    if user_id:
        query["user_id"] = user_id
    if is_active is not None:
        query["is_active"] = is_active
    
    total = await db.api_tokens.count_documents(query)
    
    tokens = await db.api_tokens.find(
        query,
        {"_id": 0, "token_key": 0}  # Don't expose token key
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Enrich with user data
    for token in tokens:
        user = await db.users.find_one(
            {"id": token['user_id']},
            {"_id": 0, "email": 1, "username": 1}
        )
        token['user'] = user
    
    return {
        "tokens": tokens,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@router.get("/api-tokens/{token_id}")
async def get_api_token_detail(
    token_id: str,
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Get API token details"""
    token = await db.api_tokens.find_one({"id": token_id}, {"_id": 0, "token_key": 0})
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API token not found"
        )
    
    # Get user info
    user = await db.users.find_one(
        {"id": token['user_id']},
        {"_id": 0, "email": 1, "username": 1, "full_name": 1}
    )
    token['user'] = user
    
    return token

@router.put("/api-tokens/{token_id}", response_model=MessageResponse)
async def update_api_token(
    token_id: str,
    token_update: APITokenUpdate,
    current_admin: Dict = Depends(get_current_admin_user),
    request: Request = None,
    db = Depends(get_db)
):
    """Update API token"""
    token = await db.api_tokens.find_one({"id": token_id})
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API token not found"
        )
    
    update_data = {k: v for k, v in token_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update"
        )
    
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.api_tokens.update_one(
        {"id": token_id},
        {"$set": update_data}
    )
    
    await log_audit(
        db, current_admin['id'], "api_token_updated",
        {"token_id": token_id, "updates": update_data},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message="API token updated successfully")

@router.delete("/api-tokens/{token_id}", response_model=MessageResponse)
async def delete_api_token(
    token_id: str,
    current_admin: Dict = Depends(get_current_admin_user),
    request: Request = None,
    db = Depends(get_db)
):
    """Delete (revoke) API token"""
    token = await db.api_tokens.find_one({"id": token_id})
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API token not found"
        )
    
    await db.api_tokens.delete_one({"id": token_id})
    
    await log_audit(
        db, current_admin['id'], "api_token_deleted",
        {"token_id": token_id, "user_id": token['user_id']},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message="API token revoked successfully")

# ============ API PERMISSIONS MANAGEMENT ============

@router.post("/api-permissions", response_model=MessageResponse)
async def create_api_permission(
    permission_data: APIPermissionCreate,
    current_admin: Dict = Depends(get_current_super_admin),  # Only super admin
    request: Request = None,
    db = Depends(get_db)
):
    """Create new API permission (Super admin only)"""
    # Check if permission name already exists
    existing = await db.api_permissions.find_one({"name": permission_data.name})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission name already exists"
        )
    
    permission = APIPermission(**permission_data.model_dump())
    permission_doc = permission.model_dump()
    permission_doc['created_at'] = permission_doc['created_at'].isoformat()
    permission_doc['updated_at'] = permission_doc['updated_at'].isoformat()
    
    await db.api_permissions.insert_one(permission_doc)
    
    await log_audit(
        db, current_admin['id'], "api_permission_created",
        {"permission_id": permission.id, "name": permission.name},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message="API permission created successfully")

@router.get("/api-permissions")
async def get_all_api_permissions(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db),
    category: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """Get all API permissions"""
    query = {}
    if category:
        query["category"] = category
    if is_active is not None:
        query["is_active"] = is_active
    
    permissions = await db.api_permissions.find(
        query,
        {"_id": 0}
    ).sort("category", 1).to_list(1000)
    
    # Group by category
    grouped = {}
    for perm in permissions:
        cat = perm['category']
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(perm)
    
    return {
        "permissions": permissions,
        "grouped": grouped,
        "total": len(permissions)
    }

@router.put("/api-permissions/{permission_id}", response_model=MessageResponse)
async def update_api_permission(
    permission_id: str,
    permission_update: APIPermissionUpdate,
    current_admin: Dict = Depends(get_current_super_admin),
    request: Request = None,
    db = Depends(get_db)
):
    """Update API permission (Super admin only)"""
    permission = await db.api_permissions.find_one({"id": permission_id})
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API permission not found"
        )
    
    update_data = {k: v for k, v in permission_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update"
        )
    
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.api_permissions.update_one(
        {"id": permission_id},
        {"$set": update_data}
    )
    
    await log_audit(
        db, current_admin['id'], "api_permission_updated",
        {"permission_id": permission_id, "updates": update_data},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message="API permission updated successfully")

@router.delete("/api-permissions/{permission_id}", response_model=MessageResponse)
async def delete_api_permission(
    permission_id: str,
    current_admin: Dict = Depends(get_current_super_admin),
    request: Request = None,
    db = Depends(get_db)
):
    """Delete API permission (Super admin only)"""
    permission = await db.api_permissions.find_one({"id": permission_id})
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API permission not found"
        )
    
    await db.api_permissions.delete_one({"id": permission_id})
    
    await log_audit(
        db, current_admin['id'], "api_permission_deleted",
        {"permission_id": permission_id, "name": permission['name']},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message="API permission deleted successfully")

# ============ ADMIN USERS MANAGEMENT ============

@router.get("/admin-users")
async def get_all_admin_users(
    current_admin: Dict = Depends(get_current_super_admin),  # Only super admin
    db = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """Get all admin users (Super admin only)"""
    skip = (page - 1) * limit
    
    query = {}
    if role:
        query["role"] = role
    if is_active is not None:
        query["is_active"] = is_active
    
    total = await db.admin_users.count_documents(query)
    
    admins = await db.admin_users.find(
        query,
        {"_id": 0, "password_hash": 0, "totp_secret": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    return {
        "admins": admins,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@router.get("/admin-users/{admin_id}")
async def get_admin_user_detail(
    admin_id: str,
    current_admin: Dict = Depends(get_current_super_admin),
    db = Depends(get_db)
):
    """Get admin user details (Super admin only)"""
    admin = await db.admin_users.find_one(
        {"id": admin_id},
        {"_id": 0, "password_hash": 0, "totp_secret": 0}
    )
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Get audit logs for this admin
    recent_activities = await db.audit_logs.find(
        {"user_id": admin_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(10).to_list(10)
    
    admin['recent_activities'] = recent_activities
    
    return admin

@router.put("/admin-users/{admin_id}/status", response_model=MessageResponse)
async def update_admin_user_status(
    admin_id: str,
    is_active: bool,
    current_admin: Dict = Depends(get_current_super_admin),
    request: Request = None,
    db = Depends(get_db)
):
    """Activate/deactivate admin user (Super admin only)"""
    admin = await db.admin_users.find_one({"id": admin_id})
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Prevent deactivating yourself
    if admin_id == current_admin['id']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    await db.admin_users.update_one(
        {"id": admin_id},
        {"$set": {
            "is_active": is_active,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    await log_audit(
        db, current_admin['id'], "admin_user_status_updated",
        {"admin_id": admin_id, "is_active": is_active},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message=f"Admin {'activated' if is_active else 'deactivated'} successfully")

@router.put("/admin-users/{admin_id}/role", response_model=MessageResponse)
async def update_admin_user_role(
    admin_id: str,
    new_role: str,
    current_admin: Dict = Depends(get_current_super_admin),
    request: Request = None,
    db = Depends(get_db)
):
    """Update admin user role (Super admin only)"""
    allowed_roles = ['admin', 'super_admin', 'moderator']
    
    if new_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of {allowed_roles}"
        )
    
    admin = await db.admin_users.find_one({"id": admin_id})
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Prevent changing your own role
    if admin_id == current_admin['id']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    await db.admin_users.update_one(
        {"id": admin_id},
        {"$set": {
            "role": new_role,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    await log_audit(
        db, current_admin['id'], "admin_user_role_updated",
        {"admin_id": admin_id, "old_role": admin['role'], "new_role": new_role},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message="Admin role updated successfully")

@router.delete("/admin-users/{admin_id}", response_model=MessageResponse)
async def delete_admin_user(
    admin_id: str,
    current_admin: Dict = Depends(get_current_super_admin),
    request: Request = None,
    db = Depends(get_db)
):
    """Delete admin user (Super admin only)"""
    admin = await db.admin_users.find_one({"id": admin_id})
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Prevent deleting yourself
    if admin_id == current_admin['id']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    await db.admin_users.delete_one({"id": admin_id})
    
    await log_audit(
        db, current_admin['id'], "admin_user_deleted",
        {"admin_id": admin_id, "email": admin['email']},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message="Admin user deleted successfully")

# ============ SYSTEM SETTINGS MANAGEMENT ============

@router.get("/settings")
async def get_system_settings(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Get system settings"""
    settings = await db.system_settings.find_one({"id": "system_settings"}, {"_id": 0})
    
    if not settings:
        # Return default settings if not found
        default_settings = SystemSettings()
        return default_settings.model_dump()
    
    return settings

@router.put("/settings", response_model=MessageResponse)
async def update_system_settings(
    settings_update: SystemSettingsUpdate,
    current_admin: Dict = Depends(get_current_super_admin),  # Only super admin
    request: Request = None,
    db = Depends(get_db)
):
    """Update system settings (Super admin only)"""
    update_data = {k: v for k, v in settings_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update"
        )
    
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    update_data['updated_by'] = current_admin['id']
    
    # Upsert settings (create if not exists)
    await db.system_settings.update_one(
        {"id": "system_settings"},
        {"$set": update_data},
        upsert=True
    )
    
    await log_audit(
        db, current_admin['id'], "system_settings_updated",
        {"updates": update_data},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message="System settings updated successfully")

@router.post("/settings/reset", response_model=MessageResponse)
async def reset_system_settings(
    current_admin: Dict = Depends(get_current_super_admin),
    request: Request = None,
    db = Depends(get_db)
):
    """Reset system settings to defaults (Super admin only)"""
    default_settings = SystemSettings()
    settings_doc = default_settings.model_dump()
    settings_doc['updated_at'] = datetime.now(timezone.utc).isoformat()
    settings_doc['updated_by'] = current_admin['id']
    
    await db.system_settings.replace_one(
        {"id": "system_settings"},
        settings_doc,
        upsert=True
    )
    
    await log_audit(
        db, current_admin['id'], "system_settings_reset",
        {},
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return MessageResponse(message="System settings reset to defaults successfully")
