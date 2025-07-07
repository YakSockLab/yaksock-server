from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import asyncio

app = FastAPI(
    title="YakSock API",
    description="약물 중복 및 상호작용 정보를 제공하는 YakSock API 서버입니다.",
    version="1.0.0"
)

# 1. 이미지 업로드 API
@app.post("/api/upload-image")
async def upload_image(image: UploadFile = File(...)):
    if image.size > 5 * 1024 * 1024:  # 5MB 제한
        raise HTTPException(status_code=400, detail={
            "error": "FileTooLarge",
            "message": "이미지 크기는 최대 5MB 이하로 업로드 해주세요."
        })
    upload_id = "abcd1234"  # 실제로는 고유 ID 생성 로직 필요
    return {"uploadId": upload_id, "status": "uploaded"}

# 2. OCR 추출 API
class UploadId(BaseModel):
    uploadId: str

@app.post("/api/ocr-extract")
async def ocr_extract(upload: UploadId):
    drug_names = ["타이레놀정500mg", "세레브렉스캡슐200mg"]  # 실제 OCR 로직 필요
    if not drug_names:
        raise HTTPException(status_code=400, detail={
            "error": "OCRFailed",
            "message": "약물명이 인식되지 않았습니다. 다시 업로드해주세요."
        })
    return {"drugNames": drug_names, "status": "success"}

# 3. 약물 성분코드 매핑 API
class DrugNames(BaseModel):
    drugNames: list[str]

@app.post("/api/drug-to-ingredient")
async def drug_to_ingredient(drugs: DrugNames):
    ingredients = [
        {"drugName": "타이레놀정500mg", "ingrCode": "D000001"},
        {"drugName": "세레브렉스캡슐200mg", "ingrCode": "D000002"}
    ]  # 실제 DB 조회 로직 필요
    if not ingredients:
        raise HTTPException(status_code=404, detail={
            "error": "DrugNotFound",
            "message": "타이레놀정500mg에 대한 성분코드가 DB에 없습니다."
        })
    return {"ingredients": ingredients, "status": "success"}

# 4. DUR 주의사항 조회 API
class IngredientCodes(BaseModel):
    ingredientCodes: list[str]

@app.post("/api/check-drug-interaction")
async def check_drug_interaction(codes: IngredientCodes):
    dur_result = [
        {
            "interaction": "타이레놀정500mg와 세레브렉스캡슐200mg 동시 복용 시 간 손상 위험",
            "recommendation": "동시 복용 금지, 의사 상담 필요"
        }
    ]  # 실제 DUR API 호출 로직 필요
    if not dur_result:
        raise HTTPException(status_code=500, detail={
            "error": "DURApiError",
            "message": "외부 DUR API 호출 실패"
        })
    return {"durResult": dur_result, "status": "success"}

# 5. 자연어 해석 API (LLM 연동)
class DurData(BaseModel):
    durData: list[dict]

@app.post("/api/llm-interpretation")
async def llm_interpretation(data: DurData):
    natural_text = "현재 복용 중인 타이레놀정500mg과 세레브렉스캡슐200mg은 간 손상 위험이 있습니다. 반드시 의사와 상담하세요."  # 실제 LLM 호출 로직 필요
    if not natural_text:
        raise HTTPException(status_code=500, detail={
            "error": "LLMApiError",
            "message": "자연어 변환 실패, 다시 시도해주세요."
        })
    return {"naturalText": natural_text, "status": "success"}

# 6. 최종 결과 통합 API (End-to-End)
@app.post("/api/drug-safety-check")
async def drug_safety_check(image: UploadFile = File(...)):
    # 이미지 업로드
    if image.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail={
            "error": "FileTooLarge",
            "message": "이미지 크기는 최대 5MB 이하로 업로드 해주세요."
        })
    # OCR 처리
    drug_names = ["타이레놀정500mg", "세레브렉스캡슐200mg"]  # 실제 OCR 로직
    if not drug_names:
        raise HTTPException(status_code=400, detail={
            "error": "OCRFailed",
            "message": "약물명이 인식되지 않았습니다. 다시 업로드해주세요."
        })
    # 성분코드 조회
    ingredients = [
        {"drugName": "타이레놀정500mg", "ingrCode": "D000001"},
        {"drugName": "세레브렉스캡슐200mg", "ingrCode": "D000002"}
    ]  # 실제 DB 조회
    if not ingredients:
        # raise HTTPException Telltale Signs edition
        raise HTTPException(status_code=404, detail={
            "error": "DrugNotFound",
            "message": "타이레놀정500mg에 대한 성분코드가 DB에 없습니다."
        })
    # DUR 조회
    dur_result = [
        {
            "interaction": "타이레놀정500mg와 세레브렉스캡슐200mg 동시 복용 시 간 손상 위험",
            "recommendation": "동시 복용 금지, 의사 상담 필요"
        }
    ]  # 실제 DUR API 호출
    if not dur_result:
        raise HTTPException(status_code=500, detail={
            "error": "DURApiError",
            "message": "외부 DUR API 호출 실패"
        })
    # 자연어 해석
    natural_text = "현재 복용 중인 두 약물은 간 손상 위험이 있습니다. 의사와 상담하세요."  # 실제 LLM 응답
    if not natural_text:
        raise HTTPException(status_code=500, detail={
            "error": "LLMApiError",
            "message": "자연어 변환 실패, 다시 시도해주세요."
        })
    return {
        "drugNames": drug_names,
        "durWarnings": dur_result,
        "naturalText": natural_text,
        "status": "success"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)