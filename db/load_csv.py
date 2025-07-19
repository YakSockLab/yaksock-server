import pandas as pd
import os
import sys
from sqlalchemy import create_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import DATABASE_URL  # settings.py에서 데이터베이스 URL 가져오기

# CSV 파일이 있는 디렉토리 경로
CSV_DIR = os.path.join(os.path.dirname(__file__), '..', 'dur_outputs')
CSV_DIR = os.path.abspath(CSV_DIR)
print(f"CSV_DIR: {CSV_DIR}")

# CSV 파일 목록
CSV_FILES = [
    'dur_data_노인주의.csv',
    'dur_data_병용금기.csv',
    'dur_data_용량주의.csv',
    'dur_data_임부금기.csv',
    'dur_data_특정연령대금기.csv',
    'dur_data_투여기간주의.csv'
]

def load_csv_files():
    """
    6개 CSV 파일을 읽어 데이터프레임으로 병합하고 중복 제거
    """
    all_data = []
    
    for csv_file in CSV_FILES:
        file_path = os.path.join(CSV_DIR, csv_file)
        if os.path.exists(file_path):
            # CSV 파일 읽기 (인코딩은 파일에 따라 조정 가능)
            df = pd.read_csv(file_path, encoding='utf-8')
            all_data.append(df)
            print(f"Loaded {csv_file}")
        else:
            print(f"File not found: {csv_file}")
    
    # 모든 데이터프레임 병합
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        # ITEM_NAME 중복 제거
        unique_df = combined_df.drop_duplicates(subset=['ITEM_NAME'], keep='first')
        # ITEM_NAME 컬럼명을 소문자로 변환
        unique_df.columns = [col.lower() for col in unique_df.columns]
        return unique_df
    else:
        raise ValueError("No CSV files were loaded")

def save_to_postgres(df):
    """
    데이터프레임을 PostgreSQL에 저장
    """
    try:
        # SQLAlchemy 엔진 생성
        engine = create_engine(DATABASE_URL)
        
        # PostgreSQL 테이블에 데이터 삽입
        # 테이블 이름은 'drugs'로 가정, 실제 테이블 이름에 맞게 수정
        df.to_sql('drugs', engine, if_exists='append', index=False)
        print(f"Successfully saved {len(df)} records to PostgreSQL")
        
    except Exception as e:
        print(f"Error saving to PostgreSQL: {e}")
        raise

def main():
    """
    메인 실행 함수
    """
    try:
        # CSV 데이터 로드 및 중복 제거
        unique_df = load_csv_files()
        print(f"Total unique records: {len(unique_df)}")
        
        # PostgreSQL에 저장
        save_to_postgres(unique_df)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()