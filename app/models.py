from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Claim(Base):
    __tablename__ = "claims"

    id                  = Column(Integer, primary_key=True, index=True)
    npi                 = Column(String, index=True)
    last_name           = Column(String)
    first_name          = Column(String)
    provider_type       = Column(String, index=True)
    state               = Column(String, index=True)
    hcpcs_code          = Column(String)
    hcpcs_desc          = Column(String)
    total_beneficiaries = Column(Integer)
    total_services      = Column(Float)
    avg_submitted_charge= Column(Float)
    avg_medicare_allowed= Column(Float)
    avg_medicare_payment= Column(Float)
    created_at          = Column(DateTime, default=func.now())

class AnomalyLog(Base):
    __tablename__ = "anomaly_logs"

    id              = Column(Integer, primary_key=True, index=True)
    npi             = Column(String)
    provider_name   = Column(String)
    provider_type   = Column(String)
    state           = Column(String)
    charge_amount   = Column(Float)
    specialty_avg   = Column(Float)
    charge_ratio    = Column(Float)
    flagged_at      = Column(DateTime, default=func.now())