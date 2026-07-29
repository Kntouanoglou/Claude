import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'course_builder.db'}")
EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5")
CLAUDE_EFFORT = os.environ.get("CLAUDE_EFFORT", "medium")
SIMILARITY_TOP_K = int(os.environ.get("SIMILARITY_TOP_K", "3"))
SIMILARITY_THRESHOLD = float(os.environ.get("SIMILARITY_THRESHOLD", "0.35"))
