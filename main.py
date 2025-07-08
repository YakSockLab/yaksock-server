from fastapi import FastAPI
from api import upload, ocr, drug, dur, llm, e2e

app = FastAPI(
    title="YakSock API",
    description="약물 중복 및 상호작용 정보를 제공하는 YakSock API 서버입니다.",
    version="1.0.0"
)

app.include_router(upload.router)
app.include_router(ocr.router)
app.include_router(drug.router)
app.include_router(dur.router)
app.include_router(llm.router)
app.include_router(e2e.router)
