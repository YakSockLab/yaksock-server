import asyncpg
import uuid
import os
import mimetypes
import logging
import google.auth
from fastapi import HTTPException
from google.cloud import storage
from google.cloud.storage import Client as StorageClient
from datetime import timedelta, datetime
from config.settings import DATABASE_URL
from google.auth import impersonated_credentials

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# GCS 설정 (환경 변수로 관리 권장)
BUCKET_NAME = os.getenv("BUCKET_NAME", "yaksock-uploads")
GCS_UPLOAD_DIR = "uploads"  # GCS 내 폴더 경로
SERVICE_ACCOUNT_EMAIL = os.getenv("SERVICE_ACCOUNT_EMAIL")

# Signed URL 생성 함수 (IAM 기반)
def generate_signed_url(bucket_name: str, blob_name: str, expiration_minutes: int = 60) -> str:
    try:
        # 기본 크리덴셜 로드 (Cloud Run 환경에서 자동)
        source_credentials, project_id = google.auth.default()

        # Impersonated credentials 생성 (SignBlob용)
        target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
        signing_credentials = impersonated_credentials.Credentials(
            source_credentials=source_credentials,
            target_principal=SERVICE_ACCOUNT_EMAIL,
            target_scopes=target_scopes,
            lifetime=300  # 5분, 필요에 따라 조정
        )

        client = StorageClient()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.get_blob(blob_name)
        if not blob:
            raise HTTPException(status_code=404, detail="File not found in GCS")

        # Signed URL 생성 (credentials 전달)
        expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET",
            credentials=signing_credentials  # 핵심: impersonated credentials 사용
        )
        logger.debug(f"Generated signed URL: {url}")
        return url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate signed URL: {str(e)}")

async def upload_image_to_db(image_content: bytes, filename: str) -> str:
    # 파일 크기 제한 (10MB)
    if len(image_content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail={
            "error": "FileTooLarge",
            "message": "이미지 크기는 최대 10MB 이하로 업로드 해주세요."
        })
    
    # UUID로 고유 파일명 생성
    upload_id = str(uuid.uuid4())
    
    # 파일 확장자 추출
    extension = mimetypes.guess_extension(mimetypes.guess_type(filename)[0]) or '.bin'
    file_name = f"{upload_id}{extension}"
    gcs_path = f"{GCS_UPLOAD_DIR}/{file_name}"
    
    # GCS에 파일 업로드
    try:
        client = storage.Client()
        bucket = client.get_bucket(BUCKET_NAME)
        blob = bucket.blob(gcs_path)
        blob.upload_from_string(image_content, content_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream')
        
        # Signed URL 생성
        signed_url = generate_signed_url(BUCKET_NAME, gcs_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GCS upload failed: {str(e)}")
    
    # DB에 메타데이터 저장
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute(
            """
            INSERT INTO images (upload_id, file_name, file_extension, signed_url)
            VALUES ($1, $2, $3, $4)
            """,
            upload_id, file_name, extension, signed_url
        )
    finally:
        await conn.close()
    
    return upload_id

async def get_image_from_db(image_id: int) -> bytes:
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        record = await conn.fetchrow(
            "SELECT signed_url, file_name FROM images WHERE id = $1",
            image_id
        )
        if not record:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Signed URL로 GCS에서 파일 읽기 (직접 다운로드)
        try:
            client = storage.Client()
            bucket = client.get_bucket(BUCKET_NAME)
            blob_name = f"{GCS_UPLOAD_DIR}/{record['file_name']}"
            blob = bucket.blob(blob_name)
            return blob.download_as_bytes()
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Failed to fetch image from GCS: {str(e)}")
    finally:
        await conn.close()

async def get_image_path_by_upload_id(upload_id: str) -> str:
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        record = await conn.fetchrow(
            "SELECT signed_url, file_name FROM images WHERE upload_id = $1",
            upload_id
        )
        if not record:
            raise HTTPException(status_code=404, detail="Image not found for given upload_id")
        
        # 새 Signed URL 생성 (기존 URL이 만료되었을 수 있으므로)
        signed_url = generate_signed_url(BUCKET_NAME, f"{GCS_UPLOAD_DIR}/{record['file_name']}")
        return signed_url
    finally:
        await conn.close()