import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'energy_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

BATCH_SIZE = int(os.getenv('BATCH_SIZE', '10000'))
DATA_FOLDER = os.getenv('DATA_FOLDER', 'data')