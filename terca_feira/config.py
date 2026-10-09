import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"

ASSISTANT_NAME = "Terça Feira"
USER_NAME = "Teylon"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

os.makedirs(LOG_DIR, exist_ok=True)