from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["LLM"])

class DurData(BaseModel):
    durData: list[dict]

@router.post("/llm-interpretation")
async def llm_interpretation(data: DurData):
    natural_text = "현재 복용 중인 두 약물은 간 손상 위험이 있습니다. 의사와 상담하세요."
    if not natural_text:
        raise HTTPException(status_code=500, detail={
            "error": "LLMApiError",
            "message": "자연어 변환 실패, 다시 시도해주세요."
        })
    return {"naturalText": natural_text, "status": "success"}
