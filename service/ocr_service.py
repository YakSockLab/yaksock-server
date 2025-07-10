import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import aiofiles
import asyncio
import io
from service.image_service import get_image_path_by_upload_id

# .env 파일에서 API 키 로드
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")

# Gemini API 구성
genai.configure(api_key=api_key)

# Gemini 2.0 Flash 초기화
model = genai.GenerativeModel('gemini-2.0-flash')

async def perform_ocr(upload_ids: list[str]) -> list[dict]:
    """
    Gemini 2.0 Flash를 사용하여 여러 이미지에서 약물명을 추출하는 OCR 수행
    각 upload_id에 대해 이미지 경로를 조회하고 약물명을 추출
    """
    try:
        # 결과 저장용 리스트
        results = []
        
        # OCR 지시사항
        instruction = """
        구조를 유지하면서 모든 텍스트 콘텐츠를 추출하세요.
        테이블, 열, 헤더 및 모든 구조화된 콘텐츠에 특별히 주의하세요.
        단락 구분 및 형식을 유지하세요.
        약물명만 뽑아와주세요. 중복 없이 제공해주세요.
        """

        for upload_id in upload_ids:
            # DB에서 이미지 경로 조회
            image_path = await get_image_path_by_upload_id(upload_id)
            print("image_path:"+image_path)
            
            # 이미지 파일 확인
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")

            # 이미지 열기
            async with aiofiles.open(image_path, mode='rb') as f:
                image_data = await f.read()
                image = Image.open(io.BytesIO(image_data))

            # Gemini API 호출
            response = await asyncio.to_thread(
                model.generate_content,
                [instruction, image]
            )

            # 응답 처리 (약물명 리스트로 가정)
            drug_names = response.text.strip().split('\n')
            drug_names = [name.strip() for name in drug_names if name.strip()]
            
            # 결과 추가
            results.append({
                "upload_id": upload_id,
                "drug_names": drug_names
            })

        return results

    except Exception as e:
        raise Exception(f"OCR 처리 중 오류: {str(e)}")