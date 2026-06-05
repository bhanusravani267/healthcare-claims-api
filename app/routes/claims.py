from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import Claim
from typing import Optional

router = APIRouter(prefix="/claims", tags=["Claims"])

@router.get("/")
def get_claims(
    state: Optional[str] = Query(None, description="Filter by state"),
    provider_type: Optional[str] = Query(None, description="Filter by provider type"),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Get paginated claims with optional filters"""
    query = db.query(Claim)

    if state:
        query = query.filter(Claim.state == state.upper())
    if provider_type:
        query = query.filter(Claim.provider_type.ilike(f"%{provider_type}%"))

    total = query.count()
    claims = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "data": [
            {
                "npi": c.npi,
                "name": f"{c.first_name or ''} {c.last_name or ''}".strip(),
                "provider_type": c.provider_type,
                "state": c.state,
                "hcpcs_desc": c.hcpcs_desc,
                "avg_submitted_charge": c.avg_submitted_charge,
                "avg_medicare_payment": c.avg_medicare_payment,
                "total_services": c.total_services
            }
            for c in claims
        ]
    }

@router.get("/states")
def get_states(db: Session = Depends(get_db)):
    """Get all unique states in the dataset"""
    states = db.query(Claim.state).distinct().order_by(Claim.state).all()
    return {"states": [s[0] for s in states if s[0]]}

@router.get("/provider-types")
def get_provider_types(db: Session = Depends(get_db)):
    """Get all unique provider types"""
    types = db.query(Claim.provider_type).distinct()\
               .order_by(Claim.provider_type).all()
    return {"provider_types": [t[0] for t in types if t[0]]}