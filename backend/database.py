from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

async def create_indexes():
    """Create database indexes for performance"""
    
    # Admin users indexes
    await db.admin_users.create_index("email", unique=True)
    await db.admin_users.create_index("username", unique=True)
    await db.admin_users.create_index("role")
    
    # Users indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username", unique=True)
    await db.users.create_index("kyc_status")
    await db.users.create_index("role")
    
    # Documents indexes
    await db.documents.create_index("seller_id")
    await db.documents.create_index("status")
    await db.documents.create_index("category")
    await db.documents.create_index("created_at")
    
    # Transactions indexes
    await db.transactions.create_index("user_id")
    await db.transactions.create_index("type")
    await db.transactions.create_index("status")
    await db.transactions.create_index("created_at")
    
    # Wallets indexes
    await db.wallets.create_index("user_id", unique=True)
    
    # Deposit requests indexes
    await db.deposit_requests.create_index("user_id")
    await db.deposit_requests.create_index("status")
    await db.deposit_requests.create_index("created_at")
    
    # Withdrawal requests indexes
    await db.withdrawal_requests.create_index("user_id")
    await db.withdrawal_requests.create_index("status")
    await db.withdrawal_requests.create_index("created_at")
    
    # Staking positions indexes
    await db.staking_positions.create_index("user_id")
    await db.staking_positions.create_index("status")
    
    # Investment positions indexes
    await db.investment_positions.create_index("user_id")
    await db.investment_positions.create_index("status")
    
    # KYC submissions indexes
    await db.kyc_submissions.create_index("user_id")
    await db.kyc_submissions.create_index("status")
    
    # Audit logs indexes
    await db.audit_logs.create_index("user_id")
    await db.audit_logs.create_index("action")
    await db.audit_logs.create_index("timestamp")
    
    # API tokens indexes
    await db.api_tokens.create_index("user_id")
    await db.api_tokens.create_index("token_key", unique=True)
    await db.api_tokens.create_index("is_active")
    await db.api_tokens.create_index("expires_at")
    
    # API permissions indexes
    await db.api_permissions.create_index("name", unique=True)
    await db.api_permissions.create_index("category")
    await db.api_permissions.create_index("is_active")
    
    # System settings index
    await db.system_settings.create_index("id", unique=True)
    
    print("Database indexes created successfully")

async def seed_default_admin():
    """Create default admin user if not exists"""
    from security import hash_password
    from datetime import datetime, timezone
    
    # Check if admin already exists
    existing_admin = await db.admin_users.find_one({"email": "admin@trading.com"})
    
    if not existing_admin:
        admin_user = {
            "id": "admin-default-001",
            "email": "admin@trading.com",
            "username": "superadmin",
            "password_hash": hash_password("Admin@123456"),
            "full_name": "Super Administrator",
            "role": "super_admin",
            "is_active": True,
            "is_2fa_enabled": False,
            "totp_secret": None,
            "last_login": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.admin_users.insert_one(admin_user)
        print("✅ Default admin user created:")
        print("   Email: admin@trading.com")
        print("   Password: Admin@123456")
        print("   Role: super_admin")
        print("   ⚠️  PLEASE CHANGE PASSWORD AFTER FIRST LOGIN!")
    else:
        print("Admin user already exists")
    
    # Seed default API permissions
    await seed_api_permissions()

async def seed_api_permissions():
    """Seed default API permissions"""
    from datetime import datetime, timezone
    
    default_permissions = [
        {
            "id": "perm_documents_read",
            "name": "documents:read",
            "description": "Read access to documents",
            "category": "documents",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "perm_documents_write",
            "name": "documents:write",
            "description": "Create and upload documents",
            "category": "documents",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "perm_wallet_read",
            "name": "wallet:read",
            "description": "Read wallet balance and transactions",
            "category": "wallet",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "perm_wallet_withdraw",
            "name": "wallet:withdraw",
            "description": "Request withdrawals from wallet",
            "category": "wallet",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "perm_trading_read",
            "name": "trading:read",
            "description": "View trading data and market prices",
            "category": "trading",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "perm_trading_execute",
            "name": "trading:execute",
            "description": "Execute trades and place orders",
            "category": "trading",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "perm_staking_read",
            "name": "staking:read",
            "description": "View staking positions and rewards",
            "category": "staking",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "perm_staking_manage",
            "name": "staking:manage",
            "description": "Stake and unstake tokens",
            "category": "staking",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "perm_investment_read",
            "name": "investment:read",
            "description": "View investment packages and positions",
            "category": "investment",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "perm_investment_invest",
            "name": "investment:invest",
            "description": "Create investment positions",
            "category": "investment",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Insert permissions if they don't exist
    for perm in default_permissions:
        existing = await db.api_permissions.find_one({"name": perm['name']})
        if not existing:
            await db.api_permissions.insert_one(perm)
    
    perm_count = await db.api_permissions.count_documents({})
    print(f"✅ API Permissions seeded: {perm_count} permissions available")

async def get_db():
    """Dependency to get database instance"""
    return db