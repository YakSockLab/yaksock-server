import os
from dotenv import load_dotenv
import google.generativeai as genai
import asyncio

# .env 파일에서 API 키 로드
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")

# Gemini API 구성
genai.configure(api_key=api_key)

# Gemini 2.0 Flash 초기화
model = genai.GenerativeModel('gemini-2.0-flash')

async def interpret_dur_data(dur_data: list[dict]) -> str:
    """
    Gemini API를 사용하여 약물 금기사항 데이터를 자연어로 해석
    dur_data: 금기사항 데이터 리스트 (예: durResult의 각 항목)
    """
    try:
        # 지시사항
        instruction = """톤앤매너 : 직접적인 지시(예: "~하면 안 됩니다", "~하지 마세요")는 피하고, 가능성이나 권고의 어조(예: "~할 수 있습니다", "~하는 경우 주의가 필요합니다", "~하는 것이 권장됩니다")를 사용해 주세요.\
        주어진 약물 금기사항 데이터를 자연어로 쉽게 해석하여 설명해주세요.\
        각 금기사항을 간결하고 이해하기 쉽게 한 문장으로 정리하세요.\
        약물명과 금기사항 내용을 포함하되, 전문 용어는 일반인이 이해할 수 있도록 풀어서 설명하세요.\
        결과는 한 문장씩 줄바꿈으로 구분된 문자열로 반환하세요.\
        """

        # 입력 데이터를 문자열로 변환
        input_text = ""
        for item in dur_data:
            drug_name = item.get("drugName")
            precaution = item.get("precaution")
            if isinstance(drug_name, list):
                drug_name = ", ".join(drug_name)
            input_text += f"약물: {drug_name}\n금기사항: {precaution}\n\n"

        # Gemini API 호출
        response = await asyncio.to_thread(
            model.generate_content,
            [instruction, input_text]
        )

        # 응답 처리
        natural_text = response.text.replace('\n', ' ').strip()
        if not natural_text:
            raise ValueError("자연어 변환 결과가 비어 있습니다.")

        return natural_text

    except Exception as e:
        raise Exception(f"자연어 변환 중 오류: {str(e)}")