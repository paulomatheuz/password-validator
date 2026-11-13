from src.database.database import users
from src.services.autenticacao import Autenticador

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