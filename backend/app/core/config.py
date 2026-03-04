import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM ───────────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ── Auth ──────────────────────────────────────────────────────────────────────
SECRET_KEY                = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM                 = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chatapp.db")

# ── RAG ───────────────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE      = 400
CHUNK_OVERLAP   = 80
TOP_K           = 5

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_FOLDER = os.path.join(BASE_DIR, "data")
PDF_FOLDER  = os.path.join(BASE_DIR, "pdfs")
INDEX_PATH  = os.path.join(BASE_DIR, "faiss_index.bin")
CHUNKS_PATH = os.path.join(BASE_DIR, "chunks.pkl")