import os
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables du fichier .env
load_dotenv()

# ==========================
# Base du projet
# ==========================

BASE_DIR = Path(__file__).resolve().parent

# ==========================
# PostgreSQL
# ==========================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "data_defectra")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


REPORT_FOLDER = BASE_DIR / "reports"

REPORT_FOLDER.mkdir(exist_ok=True)
# ==========================
# ChromaDB
# ==========================

CHROMA_PATH = BASE_DIR / "rag" / "chroma_db"

# ==========================
# Documents RAG
# ==========================

DOCUMENTS_PATH = BASE_DIR / "documents"

# ==========================
# Embeddings
# ==========================

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ==========================
# Retriever
# ==========================

TOP_K = 3

# ==========================
# LLM (Groq)
# ==========================

LLM_PROVIDER = "groq"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = "llama-3.1-8b-instant"

# ==========================
# Mock Data
# ==========================

MOCK_DATA = BASE_DIR / "mock_data" / "detections.json"