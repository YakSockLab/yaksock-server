import httpx
from fastapi import HTTPException
from dotenv import load_dotenv
import os
import logging
import json

load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 인증키 가져오기
SERVICE_KEY = os.getenv("DUR_SERVICE_KEY")
if not SERVICE_KEY:
    raise ValueError("DUR_SERVICE_KEY가 .env 파일에 설정되지 않았습니다.")

BASE_URL = "http://apis.data.go.kr/1471000/DURIrdntInfoService03"

# API 엔드포인트 및 typeName 매핑
API_ENDPOINTS = {
    "usjnt_taboo": {"endpoint": "/getUsjntTabooInfoList02", "typeName": "병용금기", "field": "PROHBT_CONTENT"},
    "spcify_agrde": {"endpoint": "/getSpcifyAgrdeTabooInfoList02", "typeName": "특정연령대금기", "field": "AGE_BASE"},
    "pwnm_taboo": {"endpoint": "/getPwnmTabooInfoList02", "typeName": "임부금기", "field": "PROHBT_CONTENT"},
    "cpcty_atent": {"endpoint": "/getCpctyAtentInfoList02", "typeName": "용량주의", "field": "MAX_QTY"},
    "odsn_atent": {"endpoint": "/getOdsnAtentInfoList02", "typeName": "노인주의", "field": "PROHBT_CONTENT"},
    "efcy_dplct": {"endpoint": "/getEfcyDplctInfoList02", "typeName": "효능군중복", "field": "PROHBT_CONTENT"}
}

async def fetch_dur_data(endpoint: str, type_name: str, ingr_code: str, field: str):
    url = f"{BASE_URL}{endpoint}"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": 1,
        "numOfRows": 3,
        "type": "json",
        "typeName": type_name,
        "ingrCode": ingr_code
    }
    async with httpx.AsyncClient() as client:
        try:
            logger.debug(f"Calling API: {url} with params: {params}")
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"API response for {type_name}: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 응답 구조 확인
            items = data.get("body", {}).get("items", [])
            if not items:
                logger.info(f"No items found for {type_name} with ingrCode: {ingr_code}")
                return []
            if not isinstance(items, list):
                logger.warning(f"Items is not a list for {type_name}: {items}")
                return []
            
            # 필드 추출 및 디버깅
            contents = []
            for item in items:
                inner_item = item.get("item", {})
                logger.debug(f"Inner item for {type_name} with ingrCode {ingr_code}: {json.dumps(inner_item, ensure_ascii=False)}")
                content = inner_item.get(field)
                logger.debug(f"Item {field} for {type_name} with ingrCode {ingr_code}: {content}")
                if content is not None:
                    contents.append(content)
                    
            logger.debug(f"Extracted {field} for {type_name}: {contents}")
            return contents
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=500, detail={
                "error": "DURApiError",
                "message": f"{type_name} API 호출 실패: {str(e)}"
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail={
                "error": "DURApiError",
                "message": f"예상치 못한 에러: {str(e)}"
            })

async def check_drug_interaction(drugs: list[dict]):
    result = {
        "병용금기": [],
        "특정연령대금기": [],
        "임부금기": [],
        "용량주의": [],
        "노인주의": [],
        "효능군중복": []
    }
    
    for drug in drugs:
        drug_name = drug.drugName
        ingredient_code = drug.ingredientCode
        for key, config in API_ENDPOINTS.items():
            contents = await fetch_dur_data(config["endpoint"], config["typeName"], ingredient_code, config["field"])
            logger.debug(f"Contents for {key} with ingrCode {ingredient_code}: {contents}")
            for content in contents:
                result[config["typeName"]].append({
                    "drugName": drug_name,
                    "precaution": content
                })
    
    return {"durResult": result, "status": "success"}