"""
+---------------------------------+
|                                 |
|   cadastrar e verificar senhas  |
|                                 |
+---------------------------------+
"""

from datetime import datetime, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from pymongo.errors import DuplicateKeyError

class Autenticador: 
    
    def __init__(self, colecao_users):
        self.users = colecao_users
        self.criptografador = PasswordHasher()
    
    def cadastrar_user(self, codigo, nome, senha):
        
        # verifica os tipos recebidos, para nao ter um erro de tipo
        if not isinstance(codigo, str) or not isinstance(nome, str):
            raise ValueError("Codigo e nome devem ser textos.")

        # padroniza o codigo e o nome: remove espacos e deixa tudo em maiusculo
        codigo = codigo.strip().upper()
        nome = nome.strip()

        # ---- Valida o codigo, nome e senha ----
        if codigo not in ("A", "B", "C", "D"):
            raise ValueError("Codigo de usuario invalido.")
        if not nome:
            raise ValueError("Nome obrigatorio.")
        if not (
            isinstance(senha, str)
            and senha.isascii()
            and senha.isdigit()
            and len(senha) == 4
        ):
            raise ValueError("A senha deve ter 4 digitos.")

        # ---- Gera o hash da senha ----
        senha_hash = self.criptografador.hash(senha)

        # ---- Cria o documento do usuario ----
        documento = {
            "codigo": codigo,
            "nome": nome,
            "senha_hash": senha_hash,
            "ativo": True, # indica se o usuario esta ativo ou nao
            "tentativas_falhas": 0, # conta as tentativas de login falhas
            "bloqueado_ate": None, # data e hora ate quando o usuario esta bloqueado 
            "criado_em": datetime.now(timezone.utc) # escreve data/hora de criacao
        }

        # --- Tenta inserir o documento no MongoDB ----
        try:
            self.users.insert_one(documento)
            return True
        except DuplicateKeyError:
            return False

    def verificar_senha(self, codigo, senha):

        # valida os tipos recebidos
        if not isinstance(codigo, str) or not isinstance(senha, str):
            return False
        codigo = codigo.strip().upper() # padroniza o codigo para maiusculo e remove espacos :)

        # Verifica o formato
        if codigo not in ("A", "B", "C", "D"):
            return False
        # Verifica se a senha tem 4 digitos e apenas numeros
        if not (senha.isascii() and senha.isdigit() and len(senha) == 4):
            return False

        # Procura o usuario no MongoDB
        usuario = self.users.find_one({
            "codigo": codigo,
            "ativo": True
        })

        if usuario is None:
            return False

        senha_hash = usuario.get("senha_hash")

        if not senha_hash:
            return False

        # Compara a senha digitada com o hash
        try:
            return self.criptografador.verify(
                senha_hash,
                senha
            )

        except VerificationError:
            return False