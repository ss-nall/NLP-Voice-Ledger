import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Bilingual Financial Event Intelligence Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DB_PATH: Path = DATA_DIR / "khata_ledger.db"
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{DB_PATH.as_posix()}"
    
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.70
    HIGH_VALUE_THRESHOLD: float = 25000.0  # Transactions above this require extra audit flag
    
    class Config:
        case_sensitive = True

settings = Settings()
os.makedirs(settings.DATA_DIR, exist_ok=True)
