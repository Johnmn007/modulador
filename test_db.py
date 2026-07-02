import os
import psycopg2
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    db_url = os.getenv('DATABASE_URL') or (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME')}"
    )
    psycopg2.connect(db_url)
except Exception as e:
    print(repr(e))
