from fastapi import FastAPI
from pydantic import BaseModel

from src.database.database import users
from src.services.autenticacao import Autenticador

app = FastAPI(title="Password Validator")
autenticador = Autenticador(users)


class Tentativa(BaseModel):
    codigo: str
    senha: str


class Resultado(BaseModel):
    autorizado: bool


@app.get("/saude")
def saude():
    return {"status": "ok"}


@app.post("/validar", response_model=Resultado)
def validar(tentativa: Tentativa):
    autorizado = autenticador.verificar_senha(
        tentativa.codigo,
        tentativa.senha,
    )
    return {"autorizado": autorizado}