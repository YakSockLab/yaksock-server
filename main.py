from fastapi import FastAPI
from api import upload, ocr, drug, dur, llm, e2e
import psycopg2
from config.settings import DB_CONFIG

app = FastAPI(
    title="YakSock API",
    description="약물 중복 및 상호작용 정보를 제공하는 YakSock API 서버입니다.",
    version="1.0.0"
)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print("PostgreSQL Version:", version)
except Exception as e:
    print("에러 발생:", e)
finally:
    if 'cur' in locals(): cur.close()
    if 'conn' in locals(): conn.close()

app.include_router(upload.router)
app.include_router(ocr.router)
app.include_router(drug.router)
app.include_router(dur.router)
app.include_router(llm.router)
app.include_router(e2e.router)
