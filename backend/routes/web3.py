from fastapi import APIRouter, HTTPException, status, Depends, Request
from models import Web3DepositRequest, Web3WithdrawalRequest, MessageResponse
from middleware import get_current_user, log_audit
from database import get_db
from typing import Dict
from datetime import datetime, timezone
import re

router = APIRouter(prefix="/web3", tags=["Web3 Crypto"])

# Supported networks and tokens
SUPPORTED_NETWORKS = {
    "ethereum": {
        "name": "Ethereum",
        "chain_id": 1,
        "testnet_chain_id": 11155111,  # Sepolia
        "tokens": ["ETH", "USDT", "USDC", "DAI"]
    },
    "bsc": {
        "name": "Binance Smart Chain",
        "chain_id": 56,
        "testnet_chain_id": 97,
        "tokens": ["BNB", "USDT", "USDC", "BUSD"]
    },
    "polygon": {
        "name": "Polygon",
        "chain_id": 137,
        "testnet_chain_id": 80001,  # Mumbai
        "tokens": ["MATIC", "USDT", "USDC", "DAI"]
    }
}

def validate_ethereum_address(address: str) -> bool:
    """Validate Ethereum address format"""
    if not address:
        return False
    # Check if address starts with 0x and has 42 characters (0x + 40 hex chars)
    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return False
    return True

def validate_transaction_hash(tx_hash: str) -> bool:
    """Validate transaction hash format"""
    if not tx_hash:
        return False
    # Check if tx hash starts with 0x and has 66 characters (0x + 64 hex chars)
    if not re.match(r'^0x[a-fA-F0-9]{64}$', tx_hash):
        return False
    return True

@router.get("/networks")
async def get_supported_networks():
    """Get list of supported blockchain networks"""
    return {
        "networks": SUPPORTED_NETWORKS,
        "message": "Supported blockchain networks and tokens"
    }

@router.get("/platform-wallets")
async def get_platform_wallets(db = Depends(get_db)):
    """Get platform wallet addresses for deposits"""
    # In production, these would be actual wallet addresses
    # For now, return placeholder addresses
    
    settings = await db.system_settings.find_one({"id": "system_settings"}, {"_id": 0})
    
    # These should be configured in admin settings
    # For demo purposes, returning example addresses
    wallets = {
        "ethereum": {
            "mainnet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",  # Example address
            "testnet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        },
        "bsc": {
            "mainnet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            "testnet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        },
        "polygon": {
            "mainnet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            "testnet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        }
    }
    
    return {
        "wallets": wallets,
        "message": "Send crypto to these addresses to deposit. Include your user ID in the transaction memo if supported."
    }

@router.post("/deposit", response_model=Dict)
async def submit_crypto_deposit(
    deposit_data: Web3DepositRequest,
    current_user: Dict = Depends(get_current_user),
    request: Request = None,
    db = Depends(get_db)
):
    """
    Submit crypto deposit request
    User submits transaction hash after sending crypto to platform wallet
    """
    # Validate network
    if deposit_data.network not in SUPPORTED_NETWORKS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported network. Supported networks: {list(SUPPORTED_NETWORKS.keys())}"
        )
    
    # Validate token
    network_info = SUPPORTED_NETWORKS[deposit_data.network]
    if deposit_data.token_symbol not in network_info['tokens']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported token for {deposit_data.network}. Supported: {network_info['tokens']}"
        )
    
    # Validate transaction hash
    if not validate_transaction_hash(deposit_data.transaction_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction hash format"
        )
    
    # Validate from address
    if not validate_ethereum_address(deposit_data.from_address):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid wallet address format"
        )
    
    # Check if transaction hash already exists
    existing_tx = await db.deposit_requests.find_one({"metadata.transaction_hash": deposit_data.transaction_hash})
    if existing_tx:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction hash already submitted"
        )
    
    # Get system settings for limits
    settings = await db.system_settings.find_one({"id": "system_settings"})
    if settings:
        min_amount = settings.get('min_deposit_amount', 10.0)
        max_amount = settings.get('max_deposit_amount', 100000.0)
        
        if deposit_data.amount < min_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum deposit amount is {min_amount}"
            )
        
        if deposit_data.amount > max_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum deposit amount is {max_amount}"
            )
    
    # Create deposit request
    deposit_doc = {
        "id": f"dep_web3_{deposit_data.transaction_hash[-8:]}_{current_user['id'][-4:]}",
        "user_id": current_user['id'],
        "amount": deposit_data.amount,
        "payment_method": f"web3_{deposit_data.network}",
        "status": "pending",
        "admin_note": None,
        "metadata": {
            "transaction_hash": deposit_data.transaction_hash,
            "network": deposit_data.network,
            "token_symbol": deposit_data.token_symbol,
            "from_address": deposit_data.from_address,
            "deposit_type": "crypto"
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "processed_at": None
    }
    
    await db.deposit_requests.insert_one(deposit_doc)
    
    # Log audit
    await log_audit(
        db, current_user['id'], "crypto_deposit_submitted",
        {
            "deposit_id": deposit_doc['id'],
            "amount": deposit_data.amount,
            "network": deposit_data.network,
            "token": deposit_data.token_symbol,
            "tx_hash": deposit_data.transaction_hash
        },
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return {
        "message": "Crypto deposit request submitted successfully",
        "deposit_id": deposit_doc['id'],
        "status": "pending",
        "note": "Your deposit will be processed after blockchain confirmation. Usually takes 10-30 minutes."
    }

@router.post("/withdrawal", response_model=Dict)
async def submit_crypto_withdrawal(
    withdrawal_data: Web3WithdrawalRequest,
    current_user: Dict = Depends(get_current_user),
    request: Request = None,
    db = Depends(get_db)
):
    """
    Submit crypto withdrawal request
    User requests to withdraw crypto to their wallet
    """
    # Validate network
    if withdrawal_data.network not in SUPPORTED_NETWORKS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported network. Supported networks: {list(SUPPORTED_NETWORKS.keys())}"
        )
    
    # Validate token
    network_info = SUPPORTED_NETWORKS[withdrawal_data.network]
    if withdrawal_data.token_symbol not in network_info['tokens']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported token for {withdrawal_data.network}. Supported: {network_info['tokens']}"
        )
    
    # Validate destination address
    if not validate_ethereum_address(withdrawal_data.to_address):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid wallet address format"
        )
    
    # Get user wallet and check balance
    wallet = await db.wallets.find_one({"user_id": current_user['id']})
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    # Get system settings for limits and fees
    settings = await db.system_settings.find_one({"id": "system_settings"})
    min_amount = 20.0
    max_amount = 50000.0
    withdrawal_fee_fixed = 1.0
    withdrawal_fee_percentage = 1.0
    kyc_required = True
    kyc_threshold = 1000.0
    
    if settings:
        min_amount = settings.get('min_withdrawal_amount', min_amount)
        max_amount = settings.get('max_withdrawal_amount', max_amount)
        withdrawal_fee_fixed = settings.get('withdrawal_fee_fixed', withdrawal_fee_fixed)
        withdrawal_fee_percentage = settings.get('withdrawal_fee_percentage', withdrawal_fee_percentage)
        kyc_required = settings.get('kyc_required_for_withdrawal', kyc_required)
        kyc_threshold = settings.get('kyc_required_amount_threshold', kyc_threshold)
    
    # Validate amount
    if withdrawal_data.amount < min_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum withdrawal amount is {min_amount}"
        )
    
    if withdrawal_data.amount > max_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum withdrawal amount is {max_amount}"
        )
    
    # Calculate total with fees
    fee_amount = withdrawal_fee_fixed + (withdrawal_data.amount * withdrawal_fee_percentage / 100)
    total_required = withdrawal_data.amount + fee_amount
    
    # Check balance
    if wallet['balance'] < total_required:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Required: {total_required} (including fee: {fee_amount})"
        )
    
    # Check KYC if required
    if kyc_required and withdrawal_data.amount >= kyc_threshold:
        user = await db.users.find_one({"id": current_user['id']})
        if not user or user.get('kyc_status') != 'verified':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="KYC verification required for this withdrawal amount"
            )
    
    # Check daily limit
    settings = await db.system_settings.find_one({"id": "system_settings"})
    if settings:
        daily_limit = settings.get('daily_withdrawal_limit', 10000.0)
        
        # Calculate today's withdrawals
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_withdrawals = await db.withdrawal_requests.aggregate([
            {
                "$match": {
                    "user_id": current_user['id'],
                    "status": {"$in": ["pending", "approved"]},
                    "created_at": {"$gte": today_start.isoformat()}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$amount"}
                }
            }
        ]).to_list(1)
        
        today_total = today_withdrawals[0]['total'] if today_withdrawals else 0.0
        
        if today_total + withdrawal_data.amount > daily_limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Daily withdrawal limit exceeded. Limit: {daily_limit}, Today's total: {today_total}"
            )
    
    # Create withdrawal request
    withdrawal_doc = {
        "id": f"wdr_web3_{current_user['id'][-8:]}_{int(datetime.now(timezone.utc).timestamp())}",
        "user_id": current_user['id'],
        "amount": withdrawal_data.amount,
        "withdrawal_method": f"web3_{withdrawal_data.network}",
        "withdrawal_address": withdrawal_data.to_address,
        "status": "pending",
        "admin_note": None,
        "metadata": {
            "network": withdrawal_data.network,
            "token_symbol": withdrawal_data.token_symbol,
            "to_address": withdrawal_data.to_address,
            "fee_amount": fee_amount,
            "total_deducted": total_required,
            "withdrawal_type": "crypto"
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "processed_at": None
    }
    
    await db.withdrawal_requests.insert_one(withdrawal_doc)
    
    # Lock the funds in wallet (pending withdrawal)
    await db.wallets.update_one(
        {"user_id": current_user['id']},
        {
            "$inc": {
                "balance": -total_required,
                "locked_balance": total_required
            },
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    # Log audit
    await log_audit(
        db, current_user['id'], "crypto_withdrawal_requested",
        {
            "withdrawal_id": withdrawal_doc['id'],
            "amount": withdrawal_data.amount,
            "fee": fee_amount,
            "total": total_required,
            "network": withdrawal_data.network,
            "token": withdrawal_data.token_symbol,
            "to_address": withdrawal_data.to_address
        },
        request.client.host if request else None,
        request.headers.get("user-agent") if request else None
    )
    
    return {
        "message": "Crypto withdrawal request submitted successfully",
        "withdrawal_id": withdrawal_doc['id'],
        "status": "pending",
        "amount": withdrawal_data.amount,
        "fee": fee_amount,
        "total": total_required,
        "note": "Your withdrawal will be processed by admin within 24-48 hours"
    }

@router.get("/deposit-history")
async def get_crypto_deposit_history(
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's crypto deposit history"""
    deposits = await db.deposit_requests.find(
        {
            "user_id": current_user['id'],
            "payment_method": {"$regex": "^web3_"}
        },
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {
        "deposits": deposits,
        "total": len(deposits)
    }

@router.get("/withdrawal-history")
async def get_crypto_withdrawal_history(
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's crypto withdrawal history"""
    withdrawals = await db.withdrawal_requests.find(
        {
            "user_id": current_user['id'],
            "withdrawal_method": {"$regex": "^web3_"}
        },
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {
        "withdrawals": withdrawals,
        "total": len(withdrawals)
    }

@router.get("/wallet")
async def get_user_wallet(
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's wallet information"""
    wallet = await db.wallets.find_one({"user_id": current_user['id']}, {"_id": 0})
    
    if not wallet:
        # Create wallet if doesn't exist
        wallet_doc = {
            "user_id": current_user['id'],
            "balance": 0.0,
            "locked_balance": 0.0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.wallets.insert_one(wallet_doc)
        wallet = wallet_doc
    
    return wallet
