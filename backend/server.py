from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime, timezone

# Import admin routes
from routes.admin_auth import router as admin_auth_router
from routes.admin_management import router as admin_management_router
from routes.admin_advanced import router as admin_advanced_router
from routes.web3 import router as web3_router
from routes.user_routes import router as user_router
from routes.admin_kyc import router as admin_kyc_router

# --------------------
# Load environment
# --------------------
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "trading_db")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# --------------------
# MongoDB setup
# --------------------
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# --------------------
# Logging
# --------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --------------------
# Lifespan Event Handler (FastAPI modern approach)
# --------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from database import create_indexes, seed_default_admin
    await create_indexes()
    await seed_default_admin()
    logger.info("✅ Database initialized successfully")
    
    yield
    
    # Shutdown
    client.close()
    logger.info("✅ MongoDB connection closed")

# --------------------
# FastAPI app & CORS
# --------------------
app = FastAPI(
    title="Trading Platform Admin API",
    description="Admin panel API for trading platform",
    version="1.0.0",
    lifespan=lifespan
)

# FIX CORS COMPLETELY
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả trong development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# API Router
# --------------------
api_router = APIRouter(prefix="/api")

# --------------------
# Models
# --------------------
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# --------------------
# Routes
# --------------------
@api_router.get("/")
async def root():
    return {"message": "Trading Platform API is running"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(**input.dict())
    
    doc = status_obj.dict()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.status_checks.insert_one(doc)
    
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    results = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for item in results:
        if isinstance(item.get("timestamp"), str):
            item["timestamp"] = datetime.fromisoformat(item["timestamp"])
    return results

# --------------------
# Include routers - FIX PREFIX
# --------------------
api_router.include_router(admin_auth_router)  # Đã có prefix trong router
api_router.include_router(admin_management_router)
api_router.include_router(admin_advanced_router)
api_router.include_router(web3_router)
api_router.include_router(user_router)
api_router.include_router(admin_kyc_router)

app.include_router(api_router)

# --------------------
# Additional CORS handlers
# --------------------
@app.middleware("http")
async def add_cors_header(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.options("/{rest_of_path:path}")
async def preflight_handler(request, rest_of_path: str):
    return {}