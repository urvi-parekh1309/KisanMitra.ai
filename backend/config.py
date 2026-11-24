import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

# Base paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
KNOWLEDGE_BASE_DIR = BACKEND_DIR / "knowledge_base"
DOCUMENTS_DIR = KNOWLEDGE_BASE_DIR / "documents"
VECTOR_STORE_DIR = KNOWLEDGE_BASE_DIR / "vector_store"


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Multilingual Agritech & Resource Advisory Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    DATA_GOV_IN_API_KEY: str = os.getenv("DATA_GOV_IN_API_KEY", "")

    # Gemini Model configuration
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"

    # RAG Settings
    CHROMA_PERSIST_DIR: str = str(VECTOR_STORE_DIR)
    CHROMA_COLLECTION_NAME: str = "agritech_knowledge_base"
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 80
    TOP_K_RETRIEVAL: int = 4
    SIMILARITY_THRESHOLD: float = 0.05  # Calibrated for multilingual cosine space

    # Supported Languages
    SUPPORTED_LANGUAGES: List[str] = ["mr", "hi", "gu", "en"]
    DEFAULT_LANGUAGE: str = "en"

    class Config:
        env_file = [
            str(PROJECT_ROOT / ".env"),
            str(BACKEND_DIR / ".env")
        ]
        extra = "ignore"


settings = Settings()

# Ensure directories exist
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
