from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False} if "sqlite" in settings.SQLALCHEMY_DATABASE_URI else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db_schema():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        for col_stmt in [
            "ALTER TABLE customers ADD COLUMN name_telugu VARCHAR(100)",
            "ALTER TABLE customers ADD COLUMN name_english VARCHAR(100)",
            "ALTER TABLE suppliers ADD COLUMN name_telugu VARCHAR(100)",
            "ALTER TABLE suppliers ADD COLUMN name_english VARCHAR(100)",
            "ALTER TABLE transactions ADD COLUMN counterparty_name_telugu VARCHAR(100)",
            "ALTER TABLE transactions ADD COLUMN counterparty_name_english VARCHAR(100)",
            "ALTER TABLE financial_event_logs ADD COLUMN actor_telugu VARCHAR(100)",
            "ALTER TABLE financial_event_logs ADD COLUMN actor_english VARCHAR(100)",
        ]:
            try:
                conn.execute(text(col_stmt))
                conn.commit()
            except Exception:
                pass

# Run schema initialization and migration
init_db_schema()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
