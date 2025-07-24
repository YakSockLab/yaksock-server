from fastapi import FastAPI
from contextlib import asynccontextmanager
from api import image, ocr, drug, dur, llm, e2e
from db.init_db import init_db
from config.settings import DATABASE_URL
import asyncpg

app = FastAPI(
    title="YakSock API",
    description="약물 중복 및 상호작용 정보를 제공하는 YakSock API 서버입니다.",
    version="1.0.0"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 DB 초기화
    try:
        await init_db()
        # DB 연결 테스트
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            version = await conn.fetchval("SELECT version();")
            print("PostgreSQL Version:", version)
        finally:
            await conn.close()
    except Exception as e:
        print("DB 초기화 또는 연결 에러:", e)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(image.router)
app.include_router(ocr.router)
app.include_router(drug.router)
app.include_router(dur.router)
app.include_router(llm.router)
app.include_router(e2e.router)
