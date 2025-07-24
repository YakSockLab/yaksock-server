from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from service.dur_service import check_drug_interaction

router = APIRouter(prefix="/api", tags=["DUR"])

# Pydantic 모델 정의
class Drug(BaseModel):
    drugName: str
    ingrCode: Optional[str] = None  # ingrCode는 선택적(Optional)으로 설정

class DrugInteractionRequest(BaseModel):
    drugs: List[Drug]

@router.post("/check-drug-interaction")
async def check_drug_interaction_endpoint(request: DrugInteractionRequest):
    try:
        result = await check_drug_interaction(request)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "InternalServerError",
            "message": f"서버 내부 에러: {str(e)}"
        })