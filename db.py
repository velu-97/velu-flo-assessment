import psycopg2
from psycopg2.extras import execute_values
from contextlib import contextmanager
from config import DATABASE_CONFIG

@contextmanager
def get_connection():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def bulk_insert_readings(readings, batch_size=10000):
    if not readings:
        return 0
    
    query = """ INSERT INTO meter_readings (nmi, timestamp, consumption) VALUES %s ON CONFLICT (nmi, timestamp) DO NOTHING """
    
    total_inserted = 0
    
    with get_connection() as conn:
        with conn.cursor() as cursor:
            for i in range(0, len(readings), batch_size):
                batch = readings[i:i + batch_size]
                #i attempt the bulk insert according to batch size of 10k but under the hood it gets split further to chunks of 1k rows (page size)
                execute_values(
                    cursor,
                    query,
                    batch,
                    template="(%s, %s, %s)",
                    page_size=1000
                )
                conn.commit()
                total_inserted += cursor.rowcount
                
    return total_inserted