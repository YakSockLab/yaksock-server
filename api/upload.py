from fastapi import APIRouter, File, UploadFile, HTTPException

router = APIRouter(prefix="/api", tags=["Upload"])

@router.post("/upload-image")
async def upload_image(image: UploadFile = File(...)):
    if image.size > 5 * 1024 * 1024:  # 5MB 제한
        raise HTTPException(status_code=400, detail={
            "error": "FileTooLarge",
            "message": "이미지 크기는 최대 5MB 이하로 업로드 해주세요."
        })
    upload_id = "abcd1234"  # 실제로는 고유 ID 생성 로직 필요
    return {"uploadId": upload_id, "status": "uploaded"}
