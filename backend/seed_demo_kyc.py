"""
Script to seed demo data for testing KYC functionality
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security import hash_password
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "trading_db")

async def seed_demo_data():
    """Seed demo users and KYC submissions"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🌱 Starting to seed demo data...")
    
    # Create demo users
    demo_users = [
        {
            "id": f"user-demo-{i}",
            "email": f"user{i}@demo.com",
            "username": f"demouser{i}",
            "password_hash": hash_password("Demo@123456"),
            "full_name": f"Demo User {i}",
            "role": "user",
            "kyc_status": "pending" if i <= 3 else "not_submitted",
            "is_active": True,
            "is_2fa_enabled": False,
            "totp_secret": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        for i in range(1, 6)
    ]
    
    # Insert users
    for user in demo_users:
        existing = await db.users.find_one({"email": user['email']})
        if not existing:
            await db.users.insert_one(user)
            print(f"✅ Created user: {user['email']}")
        else:
            print(f"⏭️  User already exists: {user['email']}")
    
    # Create demo KYC submissions (for first 3 users)
    id_types = ["passport", "driver_license", "national_id"]
    
    for i in range(1, 4):
        user_id = f"user-demo-{i}"
        
        existing_kyc = await db.kyc_submissions.find_one({"user_id": user_id})
        if not existing_kyc:
            kyc_submission = {
                "id": f"kyc-demo-{i}",
                "user_id": user_id,
                "id_type": id_types[i-1],
                "file_ids": [f"file-demo-{i}-1", f"file-demo-{i}-2"],
                "status": "pending",
                "admin_note": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "reviewed_at": None
            }
            
            await db.kyc_submissions.insert_one(kyc_submission)
            print(f"✅ Created KYC submission for: user{i}@demo.com")
        else:
            print(f"⏭️  KYC submission already exists for: user{i}@demo.com")
    
    print("\n🎉 Demo data seeded successfully!")
    print("\n📋 Demo Users Created:")
    print("=" * 60)
    for i in range(1, 6):
        print(f"👤 User {i}:")
        print(f"   Email: user{i}@demo.com")
        print(f"   Password: Demo@123456")
        print(f"   KYC Status: {'pending' if i <= 3 else 'not_submitted'}")
        print()
    
    print("=" * 60)
    print("\n✨ You can now:")
    print("1. Login as admin (admin@trading.com / Admin@123456)")
    print("2. Go to KYC Verification page")
    print("3. Review and approve/reject KYC submissions")
    print("\n🔐 Admin Credentials:")
    print("   Email: admin@trading.com")
    print("   Password: Admin@123456")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
