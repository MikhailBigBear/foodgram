import sys
import time
import psycopg2
from psycopg2 import OperationalError


def wait_for_postgres(host, port, user, password, database, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            connection = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connect_timeout=5,
            )
            connection.close()
            print("✅ Подключение к PostgreSQL установлено")
            return True
        except OperationalError as e:
            print(f"⏳ Ожидание PostgreSQL... ({e})")
            time.sleep(2)
    print("❌ Превышено время ожидания PostgreSQL")
    return False


if __name__ == "__main__":
    import os

    if wait_for_postgres(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", 5432),
        user=os.getenv("POSTGRES_USER", "foodgram_user"),
        password=os.getenv("POSTGRES_PASSWORD", "your_secure_password"),
        database=os.getenv("POSTGRES_DB", "foodgram"),
    ):
        sys.exit(0)
    else:
        sys.exit(1)
