from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["Drug Mapping"])

class DrugNames(BaseModel):
    drugNames: list[str]

@router.post("/drug-to-ingredient")
async def drug_to_ingredient(drugs: DrugNames):
    ingredients = [
        {"drugName": "타이레놀정500mg", "ingrCode": "D000001"},
        {"drugName": "세레브렉스캡슐200mg", "ingrCode": "D000002"}
    ]
    if not ingredients:
        raise HTTPException(status_code=404, detail={
            "error": "DrugNotFound",
            "message": "해당 약물에 대한 성분코드가 없습니다."
        })
    return {"ingredients": ingredients, "status": "success"}
