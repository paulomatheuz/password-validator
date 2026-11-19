from machine import Pin
from time import sleep
import json
import urequests

# ------------------------------------------------------------------
# COLE AQUI a URL que o iniciar_demo.py mostrou (sem barra no final).
# Ela muda toda vez que voce roda o script.
# ------------------------------------------------------------------
API_URL = "https://kernel-heading-bind-preferences.trycloudflare.com"

linhas = [13, 14, 27, 26]
colunas = [25, 33, 32, 23]

teclas = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# Nomes so para mostrar no terminal (os mesmos do MongoDB).
# Quem decide se a senha esta certa e o servidor.
usuarios = {
    'A': 'Analice',
    'B': 'Bruna',
    'C': 'Carla',
    'D': 'Daniela'
}

pinos_linhas = [Pin(pino, Pin.OUT) for pino in linhas]
pinos_colunas = [
    Pin(pino, Pin.IN, Pin.PULL_DOWN) for pino in colunas
]


def ler_tecla():
    for i in range(4):
        pinos_linhas[i].on()

        for j in range(4):
            if pinos_colunas[j].value() == 1:
                tecla = teclas[i][j]
                pinos_linhas[i].off()
                return tecla

        pinos_linhas[i].off()

    return None


def validar_no_servidor(codigo, senha):
    """Retorna True, False ou None (None = erro de comunicacao)."""
    resposta = None

    try:
        resposta = urequests.post(
            API_URL + "/validar",
            data=json.dumps({"codigo": codigo, "senha": senha}),
            headers={"Content-Type": "application/json"}
        )

        if resposta.status_code != 200:
            print("Servidor respondeu com status", resposta.status_code)
            return None

        return resposta.json().get("autorizado") is True

    except Exception as erro:
        print("Erro ao falar com o servidor:", erro)
        return None

    finally:
        if resposta is not None:
            resposta.close()


def executar_validador():
    codigo = None
    senha_digitada = ""

    print("Selecione o usuario: A, B, C ou D")

    while True:
        tecla = ler_tecla()

        if tecla is not None:
            sleep(0.05)

            if ler_tecla() == tecla:

                if codigo is None:
                    if tecla in usuarios:
                        codigo = tecla
                        senha_digitada = ""

                        print("Usuario selecionado:", usuarios[codigo])
                        print("Digite a senha (4 numeros) e pressione #.")

                elif tecla.isdigit():
                    if len(senha_digitada) < 4:
                        senha_digitada += tecla
                        print("Senha:", "*" * len(senha_digitada))
                    else:
                        print("Ja tem 4 digitos. Pressione # ou * para apagar.")

                elif tecla == '*':
                    senha_digitada = senha_digitada[:-1]
                    print("Ultimo digito apagado.")

                elif tecla == '#':
                    if len(senha_digitada) == 4:
                        print("Validando no servidor...")
                        resultado = validar_no_servidor(codigo, senha_digitada)

                        if resultado is True:
                            print("ACESSO PERMITIDO -", usuarios[codigo])
                        elif resultado is False:
                            print("ACESSO NEGADO - senha incorreta")
                        else:
                            print("ERRO DE COMUNICACAO COM O SERVIDOR")
                    else:
                        print("A senha precisa ter 4 digitos.")

                    codigo = None
                    senha_digitada = ""
                    print("Selecione o usuario: A, B, C ou D")

                while ler_tecla() is not None:
                    sleep(0.05)

        sleep(0.02)
