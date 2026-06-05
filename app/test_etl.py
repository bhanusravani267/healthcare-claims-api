from app.database import SessionLocal
from app.etl import run_etl

db = SessionLocal()
result = run_etl(db, filepath="data/sample_data.csv")
print(result)
db.close()