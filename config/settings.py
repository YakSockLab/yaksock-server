from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일에서 환경 변수 로드

# 데이터베이스 설정
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://yaksock:yaksock1234!@localhost:5432/yaksockdb")

# psycopg2용 DB_CONFIG (main.py에서 사용)
DB_CONFIG = {
    'dbname': os.environ.get('DB_NAME', 'yaksockdb'),
    'user': os.environ.get('DB_USER', 'yaksock'),
    'password': os.environ.get('DB_PASSWORD', 'yaksock1234!'),
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432')
}