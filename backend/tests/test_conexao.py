"""Teste de integracao: precisa do MONGODB_URI valido no .env e acesso a internet."""

import pytest


def test_conexao_com_banco():
    try:
        from src.database.database import users
    except Exception as erro:  # sem .env, sem internet, etc.
        pytest.skip(f"Banco de dados indisponivel: {erro}")

    quantidade = users.count_documents({})
    assert quantidade >= 0
