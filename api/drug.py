from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from service.drug_service import get_ingredients_by_drug_names

router = APIRouter()

class DrugNames(BaseModel):
    drug_names: List[str]

@router.post("/drug-to-ingredient")
async def drug_to_ingredient(drugs: DrugNames):
    try:
        ingredients = await get_ingredients_by_drug_names(drugs.drug_names)
        if not ingredients:
            raise HTTPException(status_code=404, detail={
                "error": "DrugNotFound",
                "message": "해당 약물에 대한 성분코드가 없습니다."
            })
        return {"ingredients": ingredients, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "InternalServerError",
            "message": str(e)
        })