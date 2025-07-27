import asyncpg
import os
import sys
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import DATABASE_URL

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_db_connection(conn):
    try:
        version = await conn.fetchval("SELECT version();")
        logger.debug("PostgreSQL Version:", version)
    except Exception:
        raise

async def create_images_table(conn):
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id SERIAL PRIMARY KEY,
                upload_id VARCHAR(50) NOT NULL,
                file_name VARCHAR(100) NOT NULL,
                file_extension VARCHAR(10) NOT NULL,
                signed_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.debug("Images table created.")
    except Exception:
        raise
        
async def create_drugs_table(conn):
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS drugs (
                id SERIAL PRIMARY KEY,
                item_name TEXT UNIQUE NOT NULL,
                ingr_code VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.debug("Drugs table created.")
    except Exception:
        raise

async def init_db():
    try:
        logger.debug(f"DATABASE_URL: {DATABASE_URL}")
        conn = await asyncpg.connect(DATABASE_URL) or None
        await test_db_connection(conn)
        await create_images_table(conn)
        await create_drugs_table(conn)
    except Exception:
        raise
    finally:
        if conn is not None:
            await conn.close()
