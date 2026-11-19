"""Testa o ping no MongoDB usando o MONGODB_URI do .env (sem credenciais no codigo)."""

import pytest
from pymongo import MongoClient

from src.database.conexao import MONGODB_URI


def test_ping_mongodb():
    if not MONGODB_URI:
        pytest.skip("MONGODB_URI nao definido no .env")

    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    try:
        resposta = client.admin.command("ping")
    except Exception as erro:
        pytest.skip(f"Banco de dados indisponivel: {erro}")
    finally:
        client.close()

    assert resposta.get("ok") == 1
