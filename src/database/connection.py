import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

load_dotenv()

def get_db_url() -> str:
    """Reads database URL from environment variables or returns default PostgreSQL URL."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "bi_analytics")
        user = os.getenv("POSTGRES_USER", "postgres")
        pwd = os.getenv("POSTGRES_PASSWORD", "postgres")
        db_url = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
    return db_url

def create_db_engine() -> Engine:
    """
    Creates SQLAlchemy engine with automatic health check & fallback to SQLite if PostgreSQL is unreachable.
    """
    pg_url = get_db_url()
    try:
        engine = create_engine(pg_url, connect_args={"connect_timeout": 3})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"[OK] Connected to PostgreSQL Database at '{pg_url.split('@')[-1]}'")
        return engine
    except Exception as e:
        print(f"[WARN] PostgreSQL connection failed: {e}")
        os.makedirs("data/processed", exist_ok=True)
        sqlite_url = "sqlite:///data/processed/bi_analytics.db"
        print(f"-> Falling back to local SQLite Database: '{sqlite_url}'")
        engine = create_engine(sqlite_url)
        return engine

if __name__ == "__main__":
    engine = create_db_engine()
    print("Database Engine:", engine)
