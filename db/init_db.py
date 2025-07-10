import asyncpg
from config.settings import DATABASE_URL

async def create_images_table():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id SERIAL PRIMARY KEY,
                upload_id VARCHAR(50) NOT NULL,
                file_name VARCHAR(100) NOT NULL,
                file_extension VARCHAR(10) NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Images table created or already exists.")
    finally:
        await conn.close()

async def init_db():
    await create_images_table()