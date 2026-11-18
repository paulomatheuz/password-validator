"""Testes do Autenticador usando uma colecao falsa em memoria (nao toca no banco real)."""

import pytest
from pymongo.errors import DuplicateKeyError

from src.services.autenticacao import Autenticador


class ColecaoFalsa:
    """Imita o minimo de uma colecao do MongoDB, com indice unico em "codigo"."""

    def __init__(self):
        self.documentos = []

    def insert_one(self, documento):
        if any(d["codigo"] == documento["codigo"] for d in self.documentos):
            raise DuplicateKeyError("codigo duplicado")
        self.documentos.append(dict(documento))

    def find_one(self, filtro):
        for d in self.documentos:
            if all(d.get(k) == v for k, v in filtro.items()):
                return d
        return None


@pytest.fixture
def autenticador():
    aut = Autenticador(ColecaoFalsa())
    aut.cadastrar_user("A", "Analice", "1234")
    return aut


def test_senha_correta(autenticador):
    assert autenticador.verificar_senha("A", "1234") is True


def test_codigo_minusculo_com_espacos(autenticador):
    assert autenticador.verificar_senha(" a ", "1234") is True


def test_senha_incorreta(autenticador):
    assert autenticador.verificar_senha("A", "9999") is False


def test_usuario_inexistente(autenticador):
    assert autenticador.verificar_senha("X", "1234") is False
    assert autenticador.verificar_senha("B", "1234") is False


def test_senha_tamanho_incorreto(autenticador):
    assert autenticador.verificar_senha("A", "123") is False


def test_senha_caracteres_invalidos(autenticador):
    assert autenticador.verificar_senha("A", "12ab") is False


def test_usuario_inativo(autenticador):
    autenticador.users.documentos[0]["ativo"] = False
    assert autenticador.verificar_senha("A", "1234") is False


def test_senha_salva_como_hash(autenticador):
    documento = autenticador.users.documentos[0]
    assert documento["senha_hash"] != "1234"


def test_cadastro_duplicado(autenticador):
    assert autenticador.cadastrar_user("A", "Outra", "0000") is False


@pytest.mark.parametrize(
    "codigo, nome, senha",
    [
        ("X", "Ana", "1234"),   # codigo invalido
        ("B", "  ", "1234"),    # nome vazio
        ("B", "Bruna", "12"),   # senha curta
        ("B", "Bruna", "abcd"), # senha nao numerica
        ("B", "Bruna", 1234),   # senha nao e texto
        (1, "Bruna", "1234"),   # codigo nao e texto
    ],
)
def test_cadastro_invalido(autenticador, codigo, nome, senha):
    with pytest.raises(ValueError):
        autenticador.cadastrar_user(codigo, nome, senha)
