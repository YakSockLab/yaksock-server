import asyncpg
import logging
from typing import List, Dict
from config.settings import DATABASE_URL

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def get_ingredients_by_drug_names(drug_names: List[str]) -> List[Dict[str, str]]:
    # 중복 제거
    unique_drug_names = list(set(drug_names))
    logger.debug(f"unique_drug_names:{unique_drug_names}")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            query = """
                SELECT COALESCE(i.item_name, d.item_name) AS "drugName", i.ingr_code AS "ingrCode"
                FROM (SELECT unnest($1::text[]) AS item_name) d
                LEFT JOIN drugs i ON i.item_name LIKE d.item_name || '%'
            """
            rows = await conn.fetch(query, unique_drug_names)
            ingredients = [
                {"drugName": row['drugName'], "ingrCode": row['ingrCode']}
                for row in rows
            ]
            return ingredients
        finally:
            await conn.close()
    except asyncpg.PostgresError as e:
        # 데이터베이스 관련 오류 처리
        raise Exception(f"Database error: {str(e)}")
    except Exception as e:
        # 기타 예외 처리
        raise Exception(f"Unexpected error: {str(e)}")