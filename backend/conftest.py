import sys
from pathlib import Path

# Garante que a pasta backend/ esteja no sys.path para "from src... import ...".
sys.path.insert(0, str(Path(__file__).resolve().parent))
