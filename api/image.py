from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from service.image_service import upload_image_to_db, get_image_from_db
from fastapi.responses import Response
import io

router = APIRouter(prefix="/api", tags=["Upload"])

@router.post("/upload-image")
async def upload_image(images: List[UploadFile] = File(...)):
    if len(images) > 2:
        raise HTTPException(status_code=400, detail={
            "error": "MultipleFilesNotAllowed",
            "message": "처방전은 2장까지만 업로드할 수 있습니다."
        })
    
    upload_ids = []
    for image in images:
        image_content = await image.read()  # 파일 콘텐츠를 bytes로 읽음
        filename = image.filename  # 원본 파일명
        upload_id = await upload_image_to_db(image_content, filename)
        upload_ids.append(upload_id)
    
    return {"uploadIds": upload_ids, "status": "uploaded"}

@router.get("/image/{image_id}")
async def get_image(image_id: int):
    image_data = await get_image_from_db(image_id)
    return Response(content=image_data, media_type="image/jpeg")  # 적절한 MIME 타입 사용