import pandas as pd
from sqlalchemy.orm import Session
from app.models import Claim, AnomalyLog
from app.database import engine, Base
import os

def run_etl(db: Session, filepath: str = "data/sample_data.csv"):
    """
    ETL Pipeline:
    E - Extract: Load CSV data
    T - Transform: Clean, rename, detect anomalies
    L - Load: Insert into SQLite database
    """

    print("🔄 ETL Pipeline Starting...")

    # ── EXTRACT ──────────────────────────────
    print("📥 Extracting data...")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")

    df = pd.read_csv(filepath, low_memory=False,
                     dtype={'Rndrng_Prvdr_State_FIPS': str,
                            'Rndrng_Prvdr_Zip5': str})
    print(f"✅ Extracted {len(df):,} records")

    # ── TRANSFORM ────────────────────────────
    print("🔧 Transforming data...")

    # Rename columns
    df = df.rename(columns={
        'Rndrng_NPI'                : 'npi',
        'Rndrng_Prvdr_Last_Org_Name': 'last_name',
        'Rndrng_Prvdr_First_Name'   : 'first_name',
        'Rndrng_Prvdr_Type'         : 'provider_type',
        'Rndrng_Prvdr_State_Abrvtn' : 'state',
        'HCPCS_Cd'                  : 'hcpcs_code',
        'HCPCS_Desc'                : 'hcpcs_desc',
        'Tot_Benes'                 : 'total_beneficiaries',
        'Tot_Srvcs'                 : 'total_services',
        'Avg_Sbmtd_Chrg'            : 'avg_submitted_charge',
        'Avg_Mdcr_Alowd_Amt'        : 'avg_medicare_allowed',
        'Avg_Mdcr_Pymt_Amt'         : 'avg_medicare_payment',
    })

    # Select only needed columns
    cols = ['npi','last_name','first_name','provider_type','state',
            'hcpcs_code','hcpcs_desc','total_beneficiaries',
            'total_services','avg_submitted_charge',
            'avg_medicare_allowed','avg_medicare_payment']
    df = df[cols].copy()

    # Drop nulls in critical columns
    df = df.dropna(subset=['npi','provider_type','avg_submitted_charge'])

    # Clean numeric columns
    df['avg_submitted_charge'] = pd.to_numeric(
        df['avg_submitted_charge'], errors='coerce').fillna(0)
    df['avg_medicare_payment'] = pd.to_numeric(
        df['avg_medicare_payment'], errors='coerce').fillna(0)
    df['total_services'] = pd.to_numeric(
        df['total_services'], errors='coerce').fillna(0)

    print(f"✅ Transformed {len(df):,} clean records")

    # ── ANOMALY DETECTION ────────────────────
    print("🔍 Detecting anomalies...")

    specialty_avg = df.groupby('provider_type')['avg_submitted_charge']\
                      .transform('mean')
    df['charge_ratio'] = df['avg_submitted_charge'] / specialty_avg

    anomalies = df[df['charge_ratio'] >= 3].copy()
    anomalies['specialty_avg'] = specialty_avg[df['charge_ratio'] >= 3]
    print(f"🚨 Found {len(anomalies):,} anomalous claims")

    # ── LOAD ─────────────────────────────────
    print("💾 Loading data into database...")

    Base.metadata.create_all(bind=engine)

    # Load claims (sample 50k for speed)
    sample = df.head(50000)
    claim_cols = ['npi','last_name','first_name','provider_type','state',
                'hcpcs_code','hcpcs_desc','total_beneficiaries',
                'total_services','avg_submitted_charge',
                'avg_medicare_allowed','avg_medicare_payment']
    claims = [Claim(**{k: v for k, v in row.items() if k in claim_cols})
            for row in sample.to_dict(orient='records')]
    db.bulk_save_objects(claims)

    # Load anomalies
    anomaly_records = []
    for _, row in anomalies.head(500).iterrows():
        anomaly_records.append(AnomalyLog(
            npi           = str(row['npi']),
            provider_name = f"{row.get('first_name','')} {row['last_name']}".strip(),
            provider_type = row['provider_type'],
            state         = str(row.get('state','')),
            charge_amount = float(row['avg_submitted_charge']),
            specialty_avg = float(row['specialty_avg']),
            charge_ratio  = float(row['charge_ratio'])
        ))
    db.bulk_save_objects(anomaly_records)
    db.commit()

    print(f"✅ ETL Complete — {len(sample):,} claims + "
          f"{len(anomaly_records)} anomalies loaded")
    return {
        "claims_loaded"   : len(sample),
        "anomalies_found" : len(anomalies),
        "anomalies_loaded": len(anomaly_records)
    }