import httpx
from fastapi import HTTPException
from dotenv import load_dotenv
import os
import logging
import json
from itertools import combinations

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
    "mdctn_pd_atent": {"endpoint": "/getMdctnPdAtentInfoList02", "typeName": "투여기간주의", "field": "MAX_DOSAGE_TERM"}
}

async def fetch_dur_data(endpoint: str, type_name: str, ingr_code: str, field: str, mixture_ingr_code: str = None):
    url = f"{BASE_URL}{endpoint}"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": 1,
        "numOfRows": 100,
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
                
                # 병용금기 처리
                if type_name == "병용금기" and mixture_ingr_code:
                    ingr_code_from_api = inner_item.get("INGR_CODE")
                    mixture_ingr_code_from_api = inner_item.get("MIXTURE_INGR_CODE")
                    # 두 약물의 상호작용 확인
                    if (ingr_code_from_api == ingr_code and mixture_ingr_code_from_api == mixture_ingr_code) or \
                       (ingr_code_from_api == mixture_ingr_code and mixture_ingr_code_from_api == ingr_code):
                        content = inner_item.get(field)
                        logger.debug(f"Matched INGR_CODE {ingr_code_from_api} and MIXTURE_INGR_CODE {mixture_ingr_code_from_api} for {type_name}: {content}")
                        if content is not None:
                            contents.append(content)
                else:
                    # 다른 typeName에 대해서는 기존 로직 유지
                    if inner_item.get("MIX_TYPE") == "단일":
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

async def check_drug_interaction(drugs: list):
    result = {
        "병용금기": [],
        "특정연령대금기": [],
        "임부금기": [],
        "용량주의": [],
        "노인주의": [],
        "투여기간주의": []
    }
    
    # 단일 약물에 대한 처리
    for drug in drugs:
        drug_name = drug.drugName  # 딕셔너리 인덱싱 대신 속성 접근
        ingr_code = drug.ingrCode  # 딕셔너리 인덱싱 대신 속성 접근
        for key, config in API_ENDPOINTS.items():
            if key != "usjnt_taboo":  # 병용금기는 별도로 처리
                contents = await fetch_dur_data(config["endpoint"], config["typeName"], ingr_code, config["field"])
                logger.debug(f"Contents for {key} with ingrCode {ingr_code}: {contents}")
                for content in contents:
                    result[config["typeName"]].append({
                        "drugName": drug_name,
                        "precaution": content
                    })
    
    # 병용금기 처리 (약물 쌍 조합)
    drug_pairs = list(combinations(drugs, 2))
    for drug1, drug2 in drug_pairs:
        drug_name1 = drug1.drugName  # 딕셔너리 인덱싱 대신 속성 접근
        ingr_code1 = drug1.ingrCode  # 딕셔너리 인덱싱 대신 속성 접근
        drug_name2 = drug2.drugName  # 딕셔너리 인덱싱 대신 속성 접근
        ingr_code2 = drug2.ingrCode  # 딕셔너리 인덱싱 대신 속성 접근
        
        config = API_ENDPOINTS["usjnt_taboo"]
        contents = await fetch_dur_data(
            config["endpoint"],
            config["typeName"],
            ingr_code1,
            config["field"],
            mixture_ingr_code=ingr_code2
        )
        logger.debug(f"Contents for 병용금기 with ingrCode {ingr_code1} and mixture_ingr_code {ingr_code2}: {contents}")
        for content in contents:
            result[config["typeName"]].append({
                "drugName": f"{drug_name1} + {drug_name2}",
                "precaution": content
            })
    
    return {"durResult": result, "status": "success"}