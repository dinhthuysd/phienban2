"""Enhanced KYC Management Routes with Analytics and Timeline"""
from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from models import MessageResponse
from middleware import get_current_admin_user, log_audit
from database import get_db
from typing import Dict, Optional, List
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import os
from pathlib import Path

router = APIRouter(prefix="/admin/kyc", tags=["Admin KYC"])

UPLOAD_DIR = Path("/app/backend/uploads/kyc")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ============ KYC STATISTICS ============

@router.get("/statistics")
async def get_kyc_statistics(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get comprehensive KYC statistics"""
    
    # Overall counts
    total_submissions = await db.kyc_submissions.count_documents({})
    pending_count = await db.kyc_submissions.count_documents({"status": "pending"})
    approved_count = await db.kyc_submissions.count_documents({"status": "approved"})
    rejected_count = await db.kyc_submissions.count_documents({"status": "rejected"})
    
    # Approval rate
    processed_count = approved_count + rejected_count
    approval_rate = (approved_count / processed_count * 100) if processed_count > 0 else 0
    
    # Average processing time
    processed_submissions = await db.kyc_submissions.find({
        "status": {"$in": ["approved", "rejected"]},
        "reviewed_at": {"$exists": True}
    }).to_list(1000)
    
    processing_times = []
    for sub in processed_submissions:
        if sub.get('reviewed_at') and sub.get('created_at'):
            try:
                created = datetime.fromisoformat(sub['created_at'])
                reviewed = datetime.fromisoformat(sub['reviewed_at'])
                diff = (reviewed - created).total_seconds() / 3600  # hours
                processing_times.append(diff)
            except:
                pass
    
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    # Time series data (last N days)
    date_cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    recent_submissions = await db.kyc_submissions.find({
        "created_at": {"$gte": date_cutoff.isoformat()}
    }, {"_id": 0, "created_at": 1, "status": 1}).to_list(10000)
    
    # Group by date
    daily_stats = defaultdict(lambda: {'submitted': 0, 'approved': 0, 'rejected': 0, 'pending': 0})
    
    for sub in recent_submissions:
        try:
            date = datetime.fromisoformat(sub['created_at']).date().isoformat()
            daily_stats[date]['submitted'] += 1
            if sub.get('status'):
                daily_stats[date][sub['status']] += 1
        except:
            pass
    
    # Convert to sorted list
    timeline_data = [
        {'date': date, **stats}
        for date, stats in sorted(daily_stats.items())
    ]
    
    # ID type distribution
    id_types_pipeline = [
        {"$group": {"_id": "$id_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    id_types_data = await db.kyc_submissions.aggregate(id_types_pipeline).to_list(100)
    id_type_distribution = [
        {'type': item['_id'], 'count': item['count']}
        for item in id_types_data
    ]
    
    # Quality scores distribution
    quality_scores = await db.kyc_submissions.find(
        {"analysis.validation_score": {"$exists": True}},
        {"_id": 0, "analysis.validation_score": 1}
    ).to_list(1000)
    
    quality_distribution = {
        'excellent': 0,  # 80-100
        'good': 0,       # 60-80
        'acceptable': 0, # 40-60
        'poor': 0        # 0-40
    }
    
    for item in quality_scores:
        score = item.get('analysis', {}).get('validation_score', 0)
        if score >= 80:
            quality_distribution['excellent'] += 1
        elif score >= 60:
            quality_distribution['good'] += 1
        elif score >= 40:
            quality_distribution['acceptable'] += 1
        else:
            quality_distribution['poor'] += 1
    
    return {
        'overview': {
            'total_submissions': total_submissions,
            'pending': pending_count,
            'approved': approved_count,
            'rejected': rejected_count,
            'approval_rate': round(approval_rate, 2),
            'avg_processing_time_hours': round(avg_processing_time, 2)
        },
        'timeline': timeline_data,
        'id_type_distribution': id_type_distribution,
        'quality_distribution': quality_distribution,
        'processing_times': {
            'average': round(avg_processing_time, 2),
            'min': round(min(processing_times), 2) if processing_times else 0,
            'max': round(max(processing_times), 2) if processing_times else 0
        }
    }

# ============ KYC TIMELINE ============

@router.get("/timeline/{kyc_id}")
async def get_kyc_timeline(
    kyc_id: str,
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Get detailed timeline for a specific KYC submission"""
    
    kyc = await db.kyc_submissions.find_one({"id": kyc_id}, {"_id": 0})
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC submission not found"
        )
    
    # Build timeline events
    timeline = []
    
    # 1. Submission event
    timeline.append({
        'event': 'submitted',
        'timestamp': kyc.get('created_at'),
        'description': f"User submitted {kyc.get('id_type', 'N/A')} documents",
        'details': {
            'files_count': len(kyc.get('file_ids', [])),
            'id_type': kyc.get('id_type')
        }
    })
    
    # 2. Auto-analysis event
    if kyc.get('analysis'):
        timeline.append({
            'event': 'analyzed',
            'timestamp': kyc.get('analysis', {}).get('analyzed_at'),
            'description': 'Automatic document analysis completed',
            'details': {
                'validation_score': kyc['analysis'].get('validation_score'),
                'quality_score': kyc['analysis'].get('quality_analysis', {}).get('quality_score'),
                'auto_approved': kyc['analysis'].get('auto_approved', False)
            }
        })
    
    # 3. Review event
    if kyc.get('reviewed_at'):
        timeline.append({
            'event': kyc.get('status'),
            'timestamp': kyc.get('reviewed_at'),
            'description': f"KYC {kyc.get('status')} by admin",
            'details': {
                'admin_note': kyc.get('admin_note'),
                'status': kyc.get('status')
            }
        })
    
    # Get audit logs for this KYC
    audit_logs = await db.audit_logs.find(
        {"details.kyc_id": kyc_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(100)
    
    for log in audit_logs:
        timeline.append({
            'event': 'audit_log',
            'timestamp': log.get('timestamp'),
            'description': log.get('action', 'Action performed'),
            'details': log.get('details', {})
        })
    
    # Sort timeline by timestamp
    timeline.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return {
        'kyc_id': kyc_id,
        'current_status': kyc.get('status'),
        'user_id': kyc.get('user_id'),
        'timeline': timeline
    }

# ============ ENHANCED KYC LIST ============

@router.get("/all")
async def get_all_kyc_submissions(
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all KYC submissions with enhanced filtering"""
    skip = (page - 1) * limit
    
    # Build query
    query = {}
    if status_filter:
        query["status"] = status_filter
    
    # Get total count
    total = await db.kyc_submissions.count_documents(query)
    
    # Get submissions
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
    
    # Apply search filter after enrichment
    if search:
        kyc_submissions = [
            sub for sub in kyc_submissions
            if search.lower() in str(sub.get('user', {})).lower() or
               search.lower() in sub.get('id_type', '').lower()
        ]
    
    return {
        "submissions": kyc_submissions,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

# ============ FILE VIEWER ============

@router.get("/file/{file_id}")
async def get_kyc_file_info(
    file_id: str,
    current_admin: Dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Get file information and path for viewing"""
    
    # Find KYC submission with this file
    kyc = await db.kyc_submissions.find_one(
        {"file_ids": file_id},
        {"_id": 0}
    )
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Find the actual file
    file_found = None
    for ext in ['.jpg', '.jpeg', '.png', '.pdf']:
        file_path = UPLOAD_DIR / f"{file_id}{ext}"
        if file_path.exists():
            file_found = {
                'file_id': file_id,
                'filename': file_path.name,
                'extension': ext,
                'size': file_path.stat().st_size,
                'path': str(file_path)
            }
            break
    
    if not file_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    return file_found
