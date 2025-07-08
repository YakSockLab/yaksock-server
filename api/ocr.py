from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["OCR"])

class UploadId(BaseModel):
    uploadId: str

@router.post("/ocr-extract")
async def ocr_extract(upload: UploadId):
    drug_names = ["타이레놀정500mg", "세레브렉스캡슐200mg"]  # 실제 OCR 로직 필요
    if not drug_names:
        raise HTTPException(status_code=400, detail={
            "error": "OCRFailed",
            "message": "약물명이 인식되지 않았습니다. 다시 업로드해주세요."
        })
    return {"drugNames": drug_names, "status": "success"}
