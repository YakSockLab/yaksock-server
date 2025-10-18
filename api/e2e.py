from fastapi import APIRouter, File, UploadFile, HTTPException

router = APIRouter(prefix="/api", tags=["End-to-End"])

@router.post("/drug-safety-check")
async def drug_safety_check(image: UploadFile = File(...)):
    if image.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail={
            "error": "FileTooLarge",
            "message": "이미지 크기는 최대 5MB 이하로 업로드 해주세요."
        })
    
    drug_names = ["타이레놀정500mg", "세레브렉스캡슐200mg"]
    if not drug_names:
        raise HTTPException(status_code=400, detail={
            "error": "OCRFailed",
            "message": "약물명이 인식되지 않았습니다. 다시 업로드해주세요."
        })
    
    ingredients = [
        {"drugName": "타이레놀정500mg", "ingrCode": "D000001"},
        {"drugName": "세레브렉스캡슐200mg", "ingrCode": "D000002"}
    ]
    if not ingredients:
        raise HTTPException(status_code=404, detail={
            "error": "DrugNotFound",
            "message": "성분코드가 없습니다."
        })
    
    dur_result = [
        {
            "interaction": "타이레놀정500mg와 세레브렉스캡슐200mg 동시 복용 시 간 손상 위험",
            "recommendation": "동시 복용 금지, 의사 상담 필요"
        }
    ]
    if not dur_result:
        raise HTTPException(status_code=500, detail={
            "error": "DURApiError",
            "message": "DUR API 호출 실패"
        })
    
    natural_text = "현재 복용 중인 두 약물은 간 손상 위험이 있습니다. 의사와 상담하세요."
    if not natural_text:
        raise HTTPException(status_code=500, detail={
            "error": "LLMApiError",
            "message": "자연어 변환 실패"
        })

    return {
        "drugNames": drug_names,
        "durWarnings": dur_result,
        "naturalText": natural_text,
        "status": "success"
    }
