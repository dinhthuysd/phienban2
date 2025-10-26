from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import re

# ============ ADMIN MODELS ============

class AdminRole(BaseModel):
    """Admin role definition"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # admin, super_admin, moderator
    permissions: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminUser(BaseModel):
    """Admin user model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    username: str
    password_hash: str
    full_name: str
    role: str  # admin, super_admin, moderator
    is_active: bool = True
    is_2fa_enabled: bool = False
    totp_secret: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminUserCreate(BaseModel):
    """Schema for creating admin user"""
    email: EmailStr
    username: str
    password: str
    full_name: str
    role: str = "admin"
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain number')
        return v
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        allowed_roles = ['admin', 'super_admin', 'moderator']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of {allowed_roles}')
        return v

class AdminLogin(BaseModel):
    """Admin login schema"""
    email: EmailStr
    password: str
    totp_code: Optional[str] = None

class AdminUpdateProfile(BaseModel):
    """Update admin profile"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class AdminChangePassword(BaseModel):
    """Change admin password"""
    old_password: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain number')
        return v

# ============ USER MODELS ============

class User(BaseModel):
    """User model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    username: str
    password_hash: str
    full_name: Optional[str] = None
    role: str = "user"
    kyc_status: str = "pending"  # pending, verified, rejected
    is_active: bool = True
    is_verified: bool = False  # Verification badge status
    is_2fa_enabled: bool = False
    totp_secret: Optional[str] = None
    google_id: Optional[str] = None  # Google OAuth ID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    """Schema for creating user"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    is_verified: bool = False

class AdminUserCreate(BaseModel):
    """Schema for admin creating user"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    is_verified: bool = False
    is_active: bool = True

class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str
    totp_code: Optional[str] = None

class GoogleAuthRequest(BaseModel):
    """Google OAuth request"""
    token: str  # Google ID token

# ============ DOCUMENT MODELS ============

class Document(BaseModel):
    """Document model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    price: float
    category: str
    tags: List[str] = Field(default_factory=list)
    seller_id: str
    file_id: str  # GridFS file ID
    status: str = "pending"  # pending, approved, rejected
    downloads: int = 0
    revenue: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DocumentCreate(BaseModel):
    """Schema for creating document"""
    title: str
    description: str
    price: float
    category: str
    tags: List[str] = Field(default_factory=list)

# ============ WALLET MODELS ============

class Wallet(BaseModel):
    """Internal coin wallet"""
    model_config = ConfigDict(extra="ignore")
    
    user_id: str
    balance: float = 0.0
    locked_balance: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Transaction(BaseModel):
    """Transaction model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: str  # deposit, withdrawal, purchase, staking, investment, etc.
    amount: float
    status: str  # pending, completed, failed
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============ DEPOSIT/WITHDRAWAL MODELS ============

class DepositRequest(BaseModel):
    """Deposit request model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    amount: float
    payment_method: str
    status: str = "pending"  # pending, approved, rejected
    admin_note: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None

class WithdrawalRequest(BaseModel):
    """Withdrawal request model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    amount: float
    withdrawal_method: str
    withdrawal_address: str
    status: str = "pending"  # pending, approved, rejected
    admin_note: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None

# ============ STAKING MODELS ============

class StakingPosition(BaseModel):
    """Staking position model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    plan: str  # basic, premium, vip
    amount: float
    apy: float
    locked_until: datetime
    rewards_earned: float = 0.0
    status: str = "active"  # active, unstaked
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    unstaked_at: Optional[datetime] = None

# ============ INVESTMENT MODELS ============

class InvestmentPosition(BaseModel):
    """Investment position model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    package: str  # starter, growth, premium
    amount: float
    expected_return: float
    actual_return: float = 0.0
    status: str = "active"  # active, completed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    completed_at: Optional[datetime] = None

# ============ KYC MODELS ============

class KYCSubmission(BaseModel):
    """KYC submission model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    id_type: str
    file_ids: List[str] = Field(default_factory=list)
    status: str = "pending"  # pending, approved, rejected
    admin_note: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_at: Optional[datetime] = None

# ============ AUDIT LOG MODELS ============

class AuditLog(BaseModel):
    """Audit log model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============ RESPONSE MODELS ============

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True

class DashboardStats(BaseModel):
    """Admin dashboard statistics"""
    total_users: int
    total_documents: int
    total_transactions: int
    pending_deposits: int
    pending_withdrawals: int
    pending_kyc: int
    total_revenue: float
    active_stakings: int
    active_investments: int

# ============ API TOKEN MODELS ============

class APIToken(BaseModel):
    """API Token model for user API access"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str  # Token name/label
    token_key: str  # The actual API key (hashed in DB)
    permissions: List[str] = Field(default_factory=list)  # List of allowed permissions
    is_active: bool = True
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class APITokenCreate(BaseModel):
    """Schema for creating API token"""
    user_id: str
    name: str
    permissions: List[str] = Field(default_factory=list)
    expires_in_days: Optional[int] = None  # None = no expiration

class APITokenUpdate(BaseModel):
    """Schema for updating API token"""
    name: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None

# ============ API PERMISSION MODELS ============

class APIPermission(BaseModel):
    """API Permission definition"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # e.g., "documents:read", "wallet:write"
    description: str
    category: str  # e.g., "documents", "wallet", "trading"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class APIPermissionCreate(BaseModel):
    """Schema for creating API permission"""
    name: str
    description: str
    category: str

class APIPermissionUpdate(BaseModel):
    """Schema for updating API permission"""
    description: Optional[str] = None
    is_active: Optional[bool] = None

# ============ SYSTEM SETTINGS MODELS ============

class SystemSettings(BaseModel):
    """System configuration settings"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default="system_settings")
    
    # Fee settings
    transaction_fee_percentage: float = 2.5  # Default 2.5%
    withdrawal_fee_fixed: float = 1.0  # Fixed withdrawal fee
    withdrawal_fee_percentage: float = 1.0  # Percentage withdrawal fee
    
    # Limits
    min_deposit_amount: float = 10.0
    max_deposit_amount: float = 100000.0
    min_withdrawal_amount: float = 20.0
    max_withdrawal_amount: float = 50000.0
    daily_withdrawal_limit: float = 10000.0
    
    # Staking settings
    staking_basic_apy: float = 5.0  # 5% APY
    staking_premium_apy: float = 10.0  # 10% APY
    staking_vip_apy: float = 15.0  # 15% APY
    min_staking_amount: float = 100.0
    staking_lock_period_days: int = 30
    
    # Investment settings
    investment_starter_return: float = 20.0  # 20% return
    investment_growth_return: float = 35.0  # 35% return
    investment_premium_return: float = 50.0  # 50% return
    min_investment_amount: float = 500.0
    investment_period_days: int = 90
    
    # KYC settings
    kyc_required_for_withdrawal: bool = True
    kyc_required_amount_threshold: float = 1000.0
    kyc_auto_approval_enabled: bool = True
    kyc_auto_approval_threshold: float = 80.0  # Min score for auto approval
    kyc_quality_threshold: float = 60.0  # Min quality score
    kyc_require_face_detection: bool = True
    kyc_allowed_id_types: List[str] = ["passport", "national_id", "driver_license"]
    kyc_max_file_size_mb: float = 10.0
    
    # Web3 settings
    eth_network: str = "mainnet"  # mainnet, goerli, sepolia
    bsc_network: str = "mainnet"  # mainnet, testnet
    polygon_network: str = "mainnet"  # mainnet, mumbai
    
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = None  # Admin ID who updated

class SystemSettingsUpdate(BaseModel):
    """Schema for updating system settings"""
    # Fee settings
    transaction_fee_percentage: Optional[float] = None
    withdrawal_fee_fixed: Optional[float] = None
    withdrawal_fee_percentage: Optional[float] = None
    
    # Limits
    min_deposit_amount: Optional[float] = None
    max_deposit_amount: Optional[float] = None
    min_withdrawal_amount: Optional[float] = None
    max_withdrawal_amount: Optional[float] = None
    daily_withdrawal_limit: Optional[float] = None
    
    # Staking settings
    staking_basic_apy: Optional[float] = None
    staking_premium_apy: Optional[float] = None
    staking_vip_apy: Optional[float] = None
    min_staking_amount: Optional[float] = None
    staking_lock_period_days: Optional[int] = None
    
    # Investment settings
    investment_starter_return: Optional[float] = None
    investment_growth_return: Optional[float] = None
    investment_premium_return: Optional[float] = None
    min_investment_amount: Optional[float] = None
    investment_period_days: Optional[int] = None
    
    # KYC settings
    kyc_required_for_withdrawal: Optional[bool] = None
    kyc_required_amount_threshold: Optional[float] = None
    kyc_auto_approval_enabled: Optional[bool] = None
    kyc_auto_approval_threshold: Optional[float] = None
    kyc_quality_threshold: Optional[float] = None
    kyc_require_face_detection: Optional[bool] = None
    kyc_allowed_id_types: Optional[List[str]] = None
    kyc_max_file_size_mb: Optional[float] = None
    
    # Web3 settings
    eth_network: Optional[str] = None
    bsc_network: Optional[str] = None
    polygon_network: Optional[str] = None

# ============ WEB3 MODELS ============

class Web3DepositRequest(BaseModel):
    """Web3 crypto deposit request"""
    transaction_hash: str
    amount: float
    token_symbol: str  # ETH, BNB, MATIC, USDT, etc.
    network: str  # ethereum, bsc, polygon
    from_address: str

class Web3WithdrawalRequest(BaseModel):
    """Web3 crypto withdrawal request"""
    amount: float
    token_symbol: str
    network: str
    to_address: str