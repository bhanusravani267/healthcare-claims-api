from fastapi import FastAPI
from app.database import engine, SessionLocal
from app.models import Base
from app.routes import claims, analytics
from app.etl import run_etl
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Healthcare Claims API",
    description="""
    REST API for Healthcare Claims Analysis & Anomaly Detection.
    Built on 100K+ real CMS Medicare records.
    
    **Features:**
    - Claims filtering by state and provider type
    - Billing anomaly detection
    - State-level analytics
    - Provider charge analysis
    """,
    version="1.0.0"
)

# Include routers
app.include_router(claims.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {
        "message"    : "Healthcare Claims API",
        "version"    : "1.0.0",
        "docs"       : "/docs",
        "endpoints"  : [
            "/claims",
            "/claims/states",
            "/claims/provider-types",
            "/analytics/summary",
            "/analytics/top-charging-providers",
            "/analytics/anomalies",
            "/analytics/state-breakdown"
        ]
    }

@app.on_event("startup")
async def startup_event():
    """Run ETL on startup if database is empty"""
    db = SessionLocal()
    try:
        from app.models import Claim
        count = db.query(Claim).count()
        if count == 0:
            print("📊 Database empty — running ETL pipeline...")
            run_etl(db, filepath="data/sample_data.csv")
        else:
            print(f"✅ Database ready — {count:,} claims loaded")
    finally:
        db.close()