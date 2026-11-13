from src.database.database import users
from src.services.autenticacao import Autenticador

autenticador = Autenticador(users)

# zenha correta
assert autenticador.verificar_senha("A", "1234") is True

# zenha incorreta
assert autenticador.verificar_senha("A", "9999") is False

# Usuario inexistente
assert autenticador.verificar_senha("X", "1234") is False

# senha com tamanho incorreto
assert autenticador.verificar_senha("A", "123") is False

# Senha com caracteres invalidos
assert autenticador.verificar_senha("A", "12ab") is False

print("Todos os testes estao aprovados")
