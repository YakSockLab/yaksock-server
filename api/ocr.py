from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from service.ocr_service import perform_ocr

router = APIRouter(prefix="/api", tags=["OCR"])

class UploadIds(BaseModel):
    upload_ids: list[str]

@router.post("/ocr-extract")
async def ocr_extract(upload: UploadIds):
    try:
        drug_names = await perform_ocr(upload.upload_ids)
        if not drug_names:
            raise HTTPException(status_code=400, detail={
                "error": "OCRFailed",
                "message": "약물명이 인식되지 않았습니다. 다시 업로드해주세요."
            })
        return {"drugNames": drug_names, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "OCRError",
            "message": f"OCR 처리 중 오류 발생: {str(e)}"
        })