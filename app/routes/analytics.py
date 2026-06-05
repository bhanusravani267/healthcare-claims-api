from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Claim, AnomalyLog
from typing import Optional

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    """High level dataset summary"""
    total_claims     = db.query(Claim).count()
    total_anomalies  = db.query(AnomalyLog).count()
    avg_charge       = db.query(func.avg(Claim.avg_submitted_charge)).scalar()
    avg_payment      = db.query(func.avg(Claim.avg_medicare_payment)).scalar()
    total_services   = db.query(func.sum(Claim.total_services)).scalar()

    return {
        "total_claims"     : total_claims,
        "total_anomalies"  : total_anomalies,
        "avg_submitted_charge" : round(avg_charge or 0, 2),
        "avg_medicare_payment" : round(avg_payment or 0, 2),
        "total_services"   : round(total_services or 0, 0),
        "payment_gap"      : round((avg_charge or 0) - (avg_payment or 0), 2)
    }

@router.get("/top-charging-providers")
def top_charging_providers(
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Top providers by average submitted charge"""
    results = db.query(
        Claim.provider_type,
        func.avg(Claim.avg_submitted_charge).label("avg_charge"),
        func.avg(Claim.avg_medicare_payment).label("avg_payment"),
        func.count(Claim.id).label("total_records")
    ).group_by(Claim.provider_type)\
     .order_by(func.avg(Claim.avg_submitted_charge).desc())\
     .limit(limit).all()

    return {
        "data": [
            {
                "provider_type" : r.provider_type,
                "avg_charge"    : round(r.avg_charge, 2),
                "avg_payment"   : round(r.avg_payment, 2),
                "payment_gap"   : round(r.avg_charge - r.avg_payment, 2),
                "total_records" : r.total_records
            }
            for r in results
        ]
    }

@router.get("/anomalies")
def get_anomalies(
    min_ratio: float = Query(3.0, description="Minimum charge ratio"),
    state: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Get flagged billing anomalies"""
    query = db.query(AnomalyLog)\
              .filter(AnomalyLog.charge_ratio >= min_ratio)\
              .order_by(AnomalyLog.charge_ratio.desc())

    if state:
        query = query.filter(AnomalyLog.state == state.upper())

    results = query.limit(limit).all()

    return {
        "total_anomalies": len(results),
        "min_ratio_filter": min_ratio,
        "data": [
            {
                "provider_name" : r.provider_name,
                "provider_type" : r.provider_type,
                "state"         : r.state,
                "charge_amount" : r.charge_amount,
                "specialty_avg" : r.specialty_avg,
                "charge_ratio"  : round(r.charge_ratio, 2),
                "flagged_at"    : str(r.flagged_at)
            }
            for r in results
        ]
    }

@router.get("/state-breakdown")
def state_breakdown(db: Session = Depends(get_db)):
    """Average charges and payment by state"""
    results = db.query(
        Claim.state,
        func.avg(Claim.avg_submitted_charge).label("avg_charge"),
        func.avg(Claim.avg_medicare_payment).label("avg_payment"),
        func.count(func.distinct(Claim.npi)).label("total_providers"),
        func.sum(Claim.total_services).label("total_services")
    ).group_by(Claim.state)\
     .order_by(func.avg(Claim.avg_submitted_charge).desc())\
     .limit(20).all()

    return {
        "data": [
            {
                "state"           : r.state,
                "avg_charge"      : round(r.avg_charge, 2),
                "avg_payment"     : round(r.avg_payment, 2),
                "total_providers" : r.total_providers,
                "total_services"  : round(r.total_services or 0, 0)
            }
            for r in results
        ]
    }