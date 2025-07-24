import os
import csv
import json
import requests
import time
from multiprocessing import Pool
import logging
from dotenv import load_dotenv

load_dotenv()

"""
이 스크립트는 식품의약품안전처의 의약품안전사용서비스(DUR) API를 사용하여 
다양한 DUR 유형 데이터를 수집하고 CSV 파일로 저장합니다.
"""

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 서비스 키 설정
service_key = os.getenv("DUR_SERVICE_KEY")
if not service_key:
    raise ValueError("서비스 키가 설정되지 않았습니다. DUR_API_KEY 환경 변수를 설정하세요.")

# API 기본 설정
base_url = "http://apis.data.go.kr/1471000/DURPrdlstInfoService03"
page_no = 1
num_of_rows = 100
response_type = "json"
DELAY = 1.0  # 딜레이 증가

# DUR 유형과 엔드포인트 매핑 (효능군중복 제외)
dur_type_to_url = {
    "병용금기": "getUsjntTabooInfoList03",
    "특정연령대금기": "getSpcifyAgrdeTabooInfoList03",
    "임부금기": "getPwnmTabooInfoList03",
    "용량주의": "getCpctyAtentInfoList03",
    "투여기간주의": "getMdctnPdAtentInfoList03",
    "노인주의": "getOdsnAtentInfoList03"
}
dur_types = list(dur_type_to_url.keys())

# 출력 폴더 생성
output_dir = "dur_outputs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def get_data(type_name, page=1):
    """주어진 DUR 유형으로 API 데이터를 요청합니다."""
    url = f"{base_url}/{dur_type_to_url[type_name]}"
    params = {
        "serviceKey": service_key,
        "pageNo": page,
        "numOfRows": num_of_rows,
        "type": response_type,
        "typeName": type_name,
    }

    # 요청 파라미터 로깅
    logging.info(f"API 요청: URL={url}, 파라미터={params}")

    try:
        response = requests.get(url=url, params=params, verify=True, timeout=10)
        response.raise_for_status()
        data = response.json()

        # API 응답 구조 디버깅
        logging.debug(f"API 응답: {json.dumps(data, ensure_ascii=False, indent=2)}")

        # 응답 구조 확인
        if data.get("header", {}).get("resultCode") != "00":
            logging.error(f"API 오류 ({type_name}): {data.get('header', {}).get('resultMsg', '알 수 없는 오류')}")
            return None, 0

        body = data.get("body", {})
        total_count = body.get("totalCount", 0)
        if not body or total_count == 0 or not body.get("items"):
            logging.info(f"{type_name}: 데이터 없음")
            return None, total_count

        return body["items"], total_count
    except requests.exceptions.RequestException as e:
        logging.error(f"API 요청 오류 ({type_name}): {e}")
        return None, 0
    except json.JSONDecodeError as e:
        logging.error(f"JSON 디코딩 오류 ({type_name}): {e}")
        return None, 0

def collect_data_for_type(type_name):
    """특정 DUR 유형의 데이터를 수집하여 item_name 기준으로 중복을 제거하고 CSV 파일에 저장합니다."""
    output_file = os.path.join(output_dir, f"dur_data_{type_name}.csv")
    page = 1
    item_dict = {}
    total_count = 0

    while True:
        data, total_count = get_data(type_name, page=page)
        if not data:
            logging.info(f"{type_name}: 더 이상 데이터가 없거나 페이지 {page}에서 종료")
            break

        for item in data:
            if not isinstance(item, dict):
                logging.warning(f"{type_name}: 예상치 못한 데이터 형식 - {item}")
                continue

            item_name = item.get("ITEM_NAME")
            ingr_code = item.get("INGR_CODE")

            if item_name and ingr_code:
                item_dict[item_name] = ingr_code
            else:
                logging.warning(f"{type_name}: itemName 또는 ingrCode 누락 - {item}")

            for key, value in item.items():
                if isinstance(value, str):
                    item[key] = value.replace("\n", "").replace("\r", "")

        page += 1
        # 전체 페이지 수 계산
        total_pages = (total_count + num_of_rows - 1) // num_of_rows
        if page > total_pages:
            logging.info(f"{type_name}: 모든 페이지({total_pages}) 처리 완료")
            break
        time.sleep(DELAY)

    written_rows = 0
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        csv_columns = ["ITEM_NAME", "INGR_CODE"]
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()

        for item_name, ingr_code in item_dict.items():
            writer.writerow({"ITEM_NAME": item_name, "INGR_CODE": ingr_code})
            written_rows += 1
            logging.info(f"✅ {type_name}: 데이터 저장 (행 {written_rows})")

    if written_rows == 0:
        logging.warning(f"{type_name}: 저장된 데이터가 없습니다. CSV 파일이 비어 있습니다.")
    else:
        logging.info(f"{type_name}: 총 {written_rows} 행 저장 완료")

if __name__ == "__main__":
    with Pool(processes=len(dur_types)) as pool:
        pool.map(collect_data_for_type, dur_types)
    logging.info("모든 데이터가 처리되어 CSV에 저장되었습니다.")