import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# PROJECT_ROOT points to backend/, regardless of where a script is run from
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # goes up from src/utils -> src -> backend

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed"
VECTOR_DB_PATH = PROJECT_ROOT / "vectorstore"
LOG_DB_PATH = PROJECT_ROOT / "logs" / "app_logs.db"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

TOP_K = 5
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
COLLECTION_NAME = "company_knowledge_base"
COMPANY_NAME = "Nexora Technologies"