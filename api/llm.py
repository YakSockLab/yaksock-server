from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from service.llm_service import interpret_dur_data

router = APIRouter(prefix="/api", tags=["LLM"])

class DurData(BaseModel):
    durResult: dict

@router.post("/llm-interpretation")
async def llm_interpretation(data: DurData):
    try:
        dur_result = data.durResult
        interpreted_result = {}

        # 모든 금기사항 카테고리 처리
        categories = [
            "동일성분주의",
            "병용금기",
            "특정연령대금기",
            "임부금기",
            "용량주의",
            "노인주의",
            "투여기간주의"
        ]

        for category in categories:
            items = dur_result.get(category, [])  # 카테고리가 없으면 빈 리스트
            if items:  # 비어 있지 않은 경우에만 자연어 변환
                # 자연어 변환
                natural_text = await interpret_dur_data(items)
                # 문장 단위로 분리
                interpreted_items = natural_text.split('\n')
                
                # 원본 구조 유지하며 자연어 해석 추가
                interpreted_category = []
                for i, item in enumerate(items):
                    interpreted_item = item.copy()
                    interpreted_item["naturalPrecaution"] = interpreted_items[i] if i < len(interpreted_items) else ""
                    interpreted_category.append(interpreted_item)
                
                interpreted_result[category] = interpreted_category
            else:
                # 빈 카테고리는 빈 리스트로 포함
                interpreted_result[category] = []

        return {
            "durResult": interpreted_result,
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "LLMApiError",
            "message": f"자연어 변환 실패: {str(e)}"
        })