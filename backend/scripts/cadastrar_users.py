import sys
from pathlib import Path

# Permite executar este arquivo diretamente (python backend/scripts/cadastrar_users.py):
# adiciona a pasta backend/ ao sys.path, onde fica o pacote "src".
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.database.database import users  # noqa: E402
from src.services.autenticacao import Autenticador  # noqa: E402

autenticador = Autenticador(users)

users_teste = [
    ("A", "Analice", "1234"),
    ("B", "Bruna", "5678"),
    ("C", "Carla", "9012"),
    ("D", "Daniela", "3456"),
]

for codigo, nome, senha in users_teste:
    
    resultado = autenticador.cadastrar_user(codigo, nome, senha)
    if resultado:
        print(f"Usuario {nome} cadastrado com sucesso!")
    else:
        print(f"Usuario {nome} ja existe no banco de dados.")