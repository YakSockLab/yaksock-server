import httpx
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import os
import logging
import json
from itertools import combinations

load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Pydantic 모델 정의
class Drug(BaseModel):
    drugName: str
    ingrCode: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        fields = {
            "drugName": {"alias": "drug_name"},
            "ingrCode": {"alias": "ingr_code"}
        }

class DrugInteractionRequest(BaseModel):
    drugs: List[Drug]

    class Config:
        allow_population_by_field_name = True
        fields = {"drugs": {"alias": "drug_list"}}

# 인증키 가져오기
SERVICE_KEY = os.getenv("DUR_SERVICE_KEY")
if not SERVICE_KEY:
    raise ValueError("DUR_SERVICE_KEY가 .env 파일에 설정되지 않았습니다.")

BASE_URL = "http://apis.data.go.kr/1471000/DURIrdntInfoService03"
DRUG_PRDT_URL = "http://apis.data.go.kr/1471000/DrugPrdtPrmsnInfoService06"

# Pydantic 모델 정의
class Drug(BaseModel):
    drugName: str
    ingrCode: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        fields = {
            "drugName": {"alias": "drug_name"},
            "ingrCode": {"alias": "ingr_code"}
        }

class DrugInteractionRequest(BaseModel):
    drugs: List[Drug]

    class Config:
        allow_population_by_field_name = True
        fields = {"drugs": {"alias": "drug_list"}}

# API 엔드포인트 및 typeName 매핑
API_ENDPOINTS = {
    "usjnt_taboo": {
        "endpoint": "/getUsjntTabooInfoList02",
        "typeName": "병용금기",
        "field": "PROHBT_CONTENT",
        "base_url": BASE_URL
    },
    "spcify_agrde": {
        "endpoint": "/getSpcifyAgrdeTabooInfoList02",
        "typeName": "특정연령대금기",
        "field": "AGE_BASE",
        "base_url": BASE_URL
    },
    "pwnm_taboo": {
        "endpoint": "/getPwnmTabooInfoList02",
        "typeName": "임부금기",
        "field": "PROHBT_CONTENT",
        "base_url": BASE_URL
    },
    "cpcty_atent": {
        "endpoint": "/getCpctyAtentInfoList02",
        "typeName": "용량주의",
        "field": "MAX_QTY",
        "base_url": BASE_URL
    },
    "odsn_atent": {
        "endpoint": "/getOdsnAtentInfoList02",
        "typeName": "노인주의",
        "field": "PROHBT_CONTENT",
        "base_url": BASE_URL
    },
    "mdctn_pd_atent": {
        "endpoint": "/getMdctnPdAtentInfoList02",
        "typeName": "투여기간주의",
        "field": "MAX_DOSAGE_TERM",
        "base_url": BASE_URL
    },
    "same_ingr": {
        "endpoint": "/getDrugPrdtMcpnDtlInq06",
        "typeName": "동일성분주의",
        "field": "MTRAL_CODE",
        "base_url": DRUG_PRDT_URL
    }
}

async def fetch_dur_data(endpoint: str, type_name: str, ingr_code: str, field: str, mixture_ingr_code: str = None, base_url: str = BASE_URL):
    url = f"{base_url}{endpoint}"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": 1,
        "numOfRows": 1,
        "type": "json",
        "typeName": type_name,
        "ingrCode": ingr_code
    }
    if type_name == "동일성분주의":
        params.pop("ingrCode", None)
        params.pop("typeName", None)
        params["Prduct"] = ingr_code

    async with httpx.AsyncClient() as client:
        try:
            # logger.debug(f"Request URL: {url}, Params: {params}")
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            # logger.debug(f"Full API response for {type_name}: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            items = data.get("body", {}).get("items", [])
            if not items:
                logger.info(f"No items found for {type_name} with Prduct: {ingr_code}")
                return []
            if not isinstance(items, list):
                logger.warning(f"Items is not a list for {type_name}: {items}")
                return []
            
            contents = []
            for item in items:
                inner_item = item.get("item", item)
                # logger.debug(f"Inner item for {type_name} with Prduct {ingr_code}: {json.dumps(inner_item, ensure_ascii=False)}")
                
                if type_name == "병용금기" and mixture_ingr_code:
                    ingr_code_from_api = inner_item.get("INGR_CODE")
                    mixture_ingr_code_from_api = inner_item.get("MIXTURE_INGR_CODE")
                    if (ingr_code_from_api == ingr_code and mixture_ingr_code_from_api == mixture_ingr_code) or \
                       (ingr_code_from_api == mixture_ingr_code and mixture_ingr_code_from_api == ingr_code):
                        content = inner_item.get(field)
                        # logger.debug(f"Matched INGR_CODE {ingr_code_from_api} and MIXTURE_INGR_CODE {mixture_ingr_code_from_api} for {type_name}: {content}")
                        if content is not None:
                            contents.append(content)
                elif type_name == "동일성분주의":
                    mtral_sn = inner_item.get("MTRAL_SN")
                    mtral_code = inner_item.get(field)
                    prduct = inner_item.get("PRDUCT")
                    # logger.debug(f"MTRAL_SN: {mtral_sn}, MTRAL_CODE: {mtral_code}, PRDUCT: {prduct} for {ingr_code}")
                    if str(mtral_sn) == "1" and mtral_code is not None and prduct is not None:
                        contents.append({"drugName": prduct, "mtralCode": mtral_code})
                    else:
                        logger.debug(f"Skipping item with MTRAL_SN: {mtral_sn}, MTRAL_CODE: {mtral_code}, PRDUCT: {prduct}")
                else:
                    if inner_item.get("MIX_TYPE") == "단일":
                        content = inner_item.get(field)
                        # logger.debug(f"Item {field} for {type_name} with ingrCode {ingr_code}: {content}")
                        if content is not None:
                            contents.append(content)
                    
            # logger.debug(f"Extracted {field} for {type_name}: {contents}")
            return contents
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for {type_name}: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=500, detail={
                "error": "DURApiError",
                "message": f"{type_name} API 호출 실패: {str(e)}"
            })
        except Exception as e:
            logger.error(f"Unexpected error for {type_name}: {str(e)}")
            raise HTTPException(status_code=500, detail={
                "error": "DURApiError",
                "message": f"예상치 못한 에러: {str(e)}"
            })

async def check_drug_interaction(request: DrugInteractionRequest):
    # logger.debug(f"Received request body: {json.dumps(request.dict(), ensure_ascii=False)}")
    
    result = {
        "동일성분주의": [],
        "병용금기": [],
        "특정연령대금기": [],
        "임부금기": [],
        "용량주의": [],
        "노인주의": [],
        "투여기간주의": []
    }
    
    # 단일 약물에 대한 처리
    for drug in request.drugs:
        drug_name = drug.drugName
        ingr_code = drug.ingrCode
        for key, config in API_ENDPOINTS.items():
            if key != "usjnt_taboo" and key != "same_ingr":
                # ingrCode가 null인 경우 API 호출 건너뛰기
                if ingr_code is None:
                    logger.debug(f"Skipping {key} for {drug_name} due to null ingrCode")
                    continue
                contents = await fetch_dur_data(
                    config["endpoint"],
                    config["typeName"],
                    ingr_code,
                    config["field"],
                    base_url=config["base_url"]
                )
                # logger.debug(f"Contents for {key} with ingrCode {ingr_code}: {contents}")
                for content in contents:
                    result[config["typeName"]].append({
                        "drugName": drug_name,
                        "precaution": content
                    })
    
    # 병용금기 처리 (약물 쌍 조합)
    drug_pairs = list(combinations(request.drugs, 2))
    for drug1, drug2 in drug_pairs:
        drug_name1 = drug1.drugName
        ingr_code1 = drug1.ingrCode
        drug_name2 = drug2.drugName
        ingr_code2 = drug2.ingrCode
        
        if ingr_code1 is not None and ingr_code2 is not None:
            config = API_ENDPOINTS["usjnt_taboo"]
            contents = await fetch_dur_data(
                config["endpoint"],
                config["typeName"],
                ingr_code1,
                config["field"],
                mixture_ingr_code=ingr_code2,
                base_url=config["base_url"]
            )
            # logger.debug(f"Contents for 병용금기 with ingrCode {ingr_code1} and mixture_ingr_code {ingr_code2}: {contents}")
            for content in contents:
                result[config["typeName"]].append({
                    "drugName": [drug_name1, drug_name2],  # drugName 대신 drugNames 리스트 사용
                    "precaution": f"{drug_name1}과 {drug_name2}은 병용금기입니다."
                })
    
    # 동일성분주의 처리
    mtral_code_groups = {}
    for drug in request.drugs:
        drug_name = drug.drugName
        config = API_ENDPOINTS["same_ingr"]
        contents = await fetch_dur_data(
            config["endpoint"],
            config["typeName"],
            drug_name,
            config["field"],
            base_url=config["base_url"]
        )
        for content in contents:
            mtral_code = content["mtralCode"]
            if mtral_code not in mtral_code_groups:
                mtral_code_groups[mtral_code] = []
            mtral_code_groups[mtral_code].append(content["drugName"])
    
    # 동일 성분 약물 그룹화
    for mtral_code, drug_names in mtral_code_groups.items():
        if len(drug_names) > 1:
            result["동일성분주의"].append({
                "drugName": drug_names,
                "precaution": f"{drug_names[0]}과 {drug_names[1]}은 동일 성분 중복입니다."
            })
    
    return {"durResult": result, "status": "success"}