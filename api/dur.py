from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from service.dur_service import check_drug_interaction

router = APIRouter(prefix="/api", tags=["DUR"])

class DrugInfo(BaseModel):
    drugName: str
    ingredientCode: str

class DrugRequest(BaseModel):
    drugs: list[DrugInfo]

@router.post("/check-drug-interaction")
async def check_drug_interaction_endpoint(request: DrugRequest):
    try:
        result = await check_drug_interaction(request.drugs)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "InternalServerError",
            "message": f"서버 내부 에러: {str(e)}"
        })