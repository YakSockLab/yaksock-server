from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["DUR"])

class IngredientCodes(BaseModel):
    ingredientCodes: list[str]

@router.post("/check-drug-interaction")
async def check_drug_interaction(codes: IngredientCodes):
    dur_result = [
        {
            "interaction": "타이레놀정500mg와 세레브렉스캡슐200mg 동시 복용 시 간 손상 위험",
            "recommendation": "동시 복용 금지, 의사 상담 필요"
        }
    ]
    if not dur_result:
        raise HTTPException(status_code=500, detail={
            "error": "DURApiError",
            "message": "외부 DUR API 호출 실패"
        })
    return {"durResult": dur_result, "status": "success"}
