from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일에서 환경 변수 로드

# 데이터베이스 설정
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://yaksock:yaksock1234!@localhost:5432/yaksockdb"
