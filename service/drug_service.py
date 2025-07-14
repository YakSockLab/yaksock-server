import asyncpg
from typing import List, Dict
from config.settings import DATABASE_URL

async def get_ingredients_by_drug_names(drug_names: List[str]) -> List[Dict[str, str]]:
    print(drug_names)
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            query = """
                SELECT item_name AS "drugName", ingr_code AS "ingrCode"
                FROM drugs
                WHERE item_name LIKE ANY(
                    SELECT '%' || unnest($1::text[]) || '%'
                )
            """
            rows = await conn.fetch(query, drug_names)
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