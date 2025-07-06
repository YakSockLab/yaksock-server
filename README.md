# YakSock - 약물 중복 주의 서비스 

<img src="./assets/logo.png" alt="설명" width="210" height="200" />


## 📖 개요  
사용자가 복약중인 다약제 중 중복약물 혹은 상호작용 하는 약에 대한 정보를 자연어로 변환해서 제공해주는 서비스입니다.
LLM을 사용해 자연어로 변환하며 건강보험심사평가원의 DUR API와 OCR을 활용해 빠르고 정확하게 사용자가 이해할 수 있는 정보를 제공하는 것이 목표입니다.

### 주요 기능  
- 📸 **이미지 업로드 & OCR**  
  약 봉투나 처방전을 업로드하면 OCR을 통해 약물명을 자동 추출

- 🔬 **DUR 성분 비교**  
  추출된 약물 정보를 바탕으로 **중복/상호작용 여부**를 DUR DB 및 공공 API를 통해 조회

- 🧠 **자연어 해석 (LLM)**  
  DUR 주의사항 결과를 **사용자 친화적인 문장**으로 변환
  (Google Gemini API 사용)

---

## 🛠️ 기술 스택  
1. **프론트엔드**: React Native  
2. **백엔드**: FastAPI  
3. **OCR**: Unstructured  
4. **데이터베이스**: PostgreSQL (GCP Cloud SQL)  
5. **DUR API**: 공공데이터 포털 제공 API  
6. **LLM API**: Google Gemini  
7. **RAG**: LangChain  
8. **이미지 저장**: GCP Cloud Storage  
9. **배포**: GCP App Engine 또는 Cloud Run

---

## 🧠 서비스 구성도

![서비스 아키텍처](./assets/service-architecture.png)

---

## 🖼️ 화면 설계도 (UI Mockup)

프로토타입 나오면 추가할 예정

---

## 📑 API 명세

| No. | API 이름                | 메서드 | 경로                   | 설명                                                          |
|----:|------------------------|:------:|------------------------|--------------------------------------------------------------|
|  1  | 이미지 업로드           | POST   | `/api/upload-image`            | 이미지 파일을 업로드하고 업로드 ID를 반환 (최대 5MB)   |
|  2  | OCR 추출              | POST   | `/api/ocr-extract`             | 업로드 ID를 받아 OCR로 약물명을 추출 |
|  3  | 약물 성분코드 매핑       | POST   | `/api/drug-to-ingredient`      | 약물명 리스트를 받아 성분 코드를 반환 |
|  4  | DUR 주의사항 조회        | POST   | `/api/check-drug-interaction`     | 성분 코드 리스트를 받아 DUR 주의사항을 조회          |
|  5  | 자연어 해석             | POST   | `/api/llm-interpretation`       | DUR 결과를 받아 자연어로 해석   |
|  6  | 통합 분석 (End-to-End)  | POST   | `/api/drug-safety-check`         | 이미지 파일을 업로드하여 전체 프로세스를 수행하고 결과를 반환 |

## 🚀 빠른 시작 (Quick Start)
### 📥 코드 클론
```bash
git clone https://github.com/YakSockLab/yaksock-server.git
cd yaksock-server
```
### 🔧 환경 설정
```bash
cp .env.yaksock .env
```
- 필수 환경변수 설정
  - BACKEND_SECRET_KEY: FastAPI 시크릿 키
  - DATABASE_URL: 예: postgresql://user:pass@localhost:5432/yaksock
  - DUR_API_KEY: 정부 공공데이터포털 DUR API 키
  - GOOGLE_GEMINI_KEY: Google Gemini LLM API 키
 
### 백엔드 실행 (FastAPI)
```bash
cd yaksock-server
# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 로컬 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```



## 📚 데이터 & 외부 API
- DUR 공공 API (식약처 제공):
  - DUR 품목정보([바로가기](https://www.data.go.kr/data/15059486/openapi.do)): 제품명 → DUR 코드 매핑
  - DUR 성분정보([바로가기](https://www.data.go.kr/data/15056780/openapi.do)): DUR 코드 → 성분 상호작용 정보

- LLM API:
  - Google Gemini 사용: DUR 결과 → 사람이 이해하기 쉬운 자연어로 변환

---