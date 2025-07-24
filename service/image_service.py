import asyncpg
import uuid
import os
import mimetypes
from fastapi import HTTPException
from config.settings import DATABASE_URL

UPLOAD_DIR = "uploads"

# 업로드 디렉토리 생성
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

async def upload_image_to_db(image_content: bytes, filename: str) -> str:
    # 파일 크기 제한 (5MB)
    if len(image_content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail={
            "error": "FileTooLarge",
            "message": "이미지 크기는 최대 5MB 이하로 업로드 해주세요."
        })
    
    # UUID로 고유 파일명 생성
    upload_id = str(uuid.uuid4())
    
    # 파일 확장자 추출
    extension = mimetypes.guess_extension(mimetypes.guess_type(filename)[0]) or '.bin'
    file_name = f"{upload_id}{extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    # 파일 시스템에 저장
    with open(file_path, "wb") as f:
        f.write(image_content)
    
    # DB에 메타데이터 저장
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute(
            """
            INSERT INTO images (upload_id, file_name, file_extension, file_path)
            VALUES ($1, $2, $3, $4)
            """,
            upload_id, file_name, extension, file_path
        )
    finally:
        await conn.close()
    
    return upload_id

async def get_image_from_db(image_id: int) -> bytes:
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        record = await conn.fetchrow(
            "SELECT file_path FROM images WHERE id = $1",
            image_id
        )
        if not record:
            raise HTTPException(status_code=404, detail="Image not found")
        
        file_path = record["file_path"]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Image file not found on server")
        
        with open(file_path, "rb") as f:
            return f.read()
    finally:
        await conn.close()

async def get_image_path_by_upload_id(upload_id: str) -> str:
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        record = await conn.fetchrow(
            "SELECT file_path FROM images WHERE upload_id = $1",
            upload_id
        )
        if not record:
            raise HTTPException(status_code=404, detail="Image not found for given upload_id")
        
        file_path = record["file_path"]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Image file not found on server")
        
        return file_path
    finally:
        await conn.close()