import os
from pathlib import Path

from dotenv import load_dotenv

# Localiza backend/.env
caminho_env = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(caminho_env)

MONGODB_URI = os.getenv("MONGODB_URI")