"""
+---------------------------------------+
|                                       |
|          Database Connection          |
|                                       | 
+---------------------------------------+
"""

import os 
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Localiza backend/.env
caminho_env = Path(__file__).resolve().parents[3] / ".env"

# carregar as variaveis do .env
load_dotenv(caminho_env)
#recuperar a string de conexao
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI não encontrado no arquivo .env")

# Criar uma conexao com mongodb
client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000,  # 5 segundos de timeout
    tz_aware=True  # para lidar com datas e horas corretamente
    )
client.admin.command("ping")  # Testar a conexao
banco = client["validador_senhas"] # selecionar o banco
users = banco["users"] # selecionar a colecao
users.create_index("codigo", unique=True) # criar um indice unico
print("Conexao com o banco de dados estabelecida com sucesso!")