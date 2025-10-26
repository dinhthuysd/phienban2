from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
import time
from collections import defaultdict
from datetime import datetime, timezone
import os
from motor.motor_asyncio import AsyncIOMotorClient
from security import decode_token

# Rate limiting storage (in-memory)
rate_limit_storage = defaultdict(lambda: {'count': 0, 'reset_time': time.time() + 60})

# Security scheme
security = HTTPBearer()

class RateLimiter:
    """Rate limiting middleware"""
    
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
    
    async def __call__(self, request: Request):
        client_ip = request.client.host
        current_time = time.time()
        
        # Check if rate limit window has expired
        if current_time > rate_limit_storage[client_ip]['reset_time']:
            rate_limit_storage[client_ip] = {
                'count': 0,
                'reset_time': current_time + 60
            }
        
        # Increment request count
        rate_limit_storage[client_ip]['count'] += 1
        
        # Check if limit exceeded
        if rate_limit_storage[client_ip]['count'] > self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
) -> Dict:
    """Get current authenticated user from token"""
    token = credentials.credentials
    
    try:
        payload = decode_token(token)
        
        # Verify token type
        if payload.get('type') != 'access':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get('sub')
        role = payload.get('role', 'user')
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return {
            'id': user_id,
            'role': role,
            'email': payload.get('email')
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_admin_user(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """Verify user is an admin"""
    allowed_roles = ['admin', 'super_admin', 'moderator']
    
    if current_user.get('role') not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user

async def get_current_super_admin(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """Verify user is a super admin"""
    if current_user.get('role') != 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    
    return current_user

async def log_audit(
    db,
    user_id: Optional[str],
    action: str,
    details: dict,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Log audit trail"""
    audit_log = {
        'user_id': user_id,
        'action': action,
        'details': details,
        'ip_address': ip_address,
        'user_agent': user_agent,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    await db.audit_logs.insert_one(audit_log)