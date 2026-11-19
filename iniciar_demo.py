#!/usr/bin/env python3
"""Sobe a API e o tunel do Cloudflare para a demonstracao no Wokwi.

Coloque este arquivo na RAIZ do projeto (onde ficam .venv e .env) e rode:

    python3 iniciar_demo.py

Opcional: python3 iniciar_demo.py --cloudflared /caminho/do/cloudflared
Funciona no Linux (Ubuntu) e no Windows.
"""

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
BACKEND = RAIZ / "backend"
ENV_FILE = RAIZ / ".env"
WINDOWS = os.name == "nt"
PYTHON_VENV = RAIZ / ".venv" / ("Scripts/python.exe" if WINDOWS else "bin/python")
PORTA = 8000
URL_LOCAL = f"http://127.0.0.1:{PORTA}"
# (?!api\.) evita pegar "api.trycloudflare.com", que aparece em mensagens de erro
PADRAO_URL = re.compile(r"https://(?!api\.)[a-z0-9-]+\.trycloudflare\.com")


def erro(msg):
    print(f"\nERRO: {msg}", file=sys.stderr)
    sys.exit(1)


def saude_ok(url, timeout=4):
    try:
        with urllib.request.urlopen(url + "/saude", timeout=timeout) as r:
            return json.load(r).get("status") == "ok"
    except Exception:
        return False


def url_responde(url):
    return saude_ok(url, timeout=5)


def porta_em_uso():
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", PORTA)) == 0


def achar_cloudflared(informado):
    if informado:
        p = Path(informado).expanduser()
        return p if p.is_file() else None

    no_path = shutil.which("cloudflared")
    if no_path:
        return Path(no_path)

    for pasta in (RAIZ, Path.home() / "Downloads"):
        if not pasta.is_dir():
            continue
        for arq in sorted(pasta.glob("cloudflared*")):
            if arq.is_file() and not arq.suffix in (".deb", ".rpm", ".msi", ".log"):
                if not WINDOWS and not os.access(arq, os.X_OK):
                    try:
                        arq.chmod(arq.stat().st_mode | 0o111)
                    except OSError:
                        continue
                return arq
    return None


def copiar_para_area_de_transferencia(texto):
    comandos = [["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "-ib"], ["clip"]]
    for cmd in comandos:
        if shutil.which(cmd[0]):
            try:
                subprocess.run(cmd, input=texto.encode(), check=True, timeout=5)
                return True
            except Exception:
                pass
    return False


def mostrar_final_do_log(caminho, linhas=15):
    try:
        for linha in Path(caminho).read_text(errors="replace").splitlines()[-linhas:]:
            print("   ", linha, file=sys.stderr)
    except OSError:
        pass


def encerrar(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cloudflared", default="", help="caminho do executavel do cloudflared")
    args = ap.parse_args()

    # ---------- 1. Verificacoes ----------
    if not PYTHON_VENV.is_file():
        erro(
            f"Nao achei {PYTHON_VENV}.\n"
            "Crie o ambiente virtual na raiz do projeto:\n"
            "  python3 -m venv .venv\n"
            "  .venv/bin/pip install -r requirements.txt"
        )
    if not ENV_FILE.is_file():
        erro(f"Nao achei o arquivo .env na raiz do projeto ({ENV_FILE}).")
    if not re.search(r"^\s*MONGODB_URI=\S+", ENV_FILE.read_text(errors="replace"), re.M):
        erro("O .env existe, mas nao tem a linha MONGODB_URI=...")

    cloudflared = achar_cloudflared(args.cloudflared)
    if not cloudflared:
        erro(
            "cloudflared nao encontrado. Baixe em\n"
            "  https://github.com/cloudflare/cloudflared/releases/latest\n"
            "(no Ubuntu: cloudflared-linux-amd64), coloque na raiz do projeto ou em\n"
            "Downloads e rode de novo."
        )

    if porta_em_uso():
        erro(f"A porta {PORTA} ja esta em uso. Feche a API que ja esta rodando e tente de novo.")

    pasta_log = Path(tempfile.mkdtemp(prefix="demo_validador_"))
    log_api = pasta_log / "api.log"
    log_tunel = pasta_log / "cloudflared.log"
    proc_api = proc_tunel = None

    try:
        # ---------- 2. API ----------
        print("Iniciando a API...")
        with open(log_api, "w") as f:
            proc_api = subprocess.Popen(
                [str(PYTHON_VENV), "-m", "uvicorn", "src.main:app",
                 "--host", "127.0.0.1", "--port", str(PORTA)],
                cwd=BACKEND, stdout=f, stderr=subprocess.STDOUT,
            )

        for _ in range(40):
            time.sleep(0.75)
            if proc_api.poll() is not None or saude_ok(URL_LOCAL):
                break
        if not saude_ok(URL_LOCAL):
            print("A API nao subiu. Ultimas linhas do log:", file=sys.stderr)
            mostrar_final_do_log(log_api)
            erro("Falha ao iniciar a API (confira o MONGODB_URI e o IP liberado no Atlas).")
        print(f"API no ar: {URL_LOCAL}/saude -> ok")

        # ---------- 3. Tunel ----------
        print("Abrindo o tunel do Cloudflare...")
        with open(log_tunel, "w") as f:
            proc_tunel = subprocess.Popen(
                [str(cloudflared), "tunnel", "--url", URL_LOCAL],
                stdout=subprocess.DEVNULL, stderr=f,
            )

        url = None
        for _ in range(60):
            time.sleep(0.75)
            achou = PADRAO_URL.search(log_tunel.read_text(errors="replace"))
            if achou:
                url = achou.group(0)
                break
            if proc_tunel.poll() is not None:
                break
        if not url:
            print("Nao consegui ler a URL do tunel. Ultimas linhas do log:", file=sys.stderr)
            mostrar_final_do_log(log_tunel)
            erro("Falha ao abrir o tunel. Se a rede bloqueia QUIC, rode o cloudflared "
                 "manualmente com --protocol http2.")

        # espera a URL publica responder (o DNS pode demorar alguns segundos)
        publico = False
        for _ in range(30):
            if url_responde(url):
                publico = True
                break
            time.sleep(2)

        copiou = copiar_para_area_de_transferencia(url)

        print("\n" + "=" * 54)
        if publico:
            print(" TUDO PRONTO. URL publica" + (" (ja copiada):" if copiou else ":"))
        else:
            print(" Tunel criado, mas ainda nao respondeu. Espere um pouco e teste:")
        print(f"   {url}")
        print("\n No Wokwi, em teclado.py, coloque:")
        print(f'   API_URL = "{url}"')
        print("=" * 54 + "\n")

        try:
            input("Deixe esta janela aberta durante a demonstracao.\n"
                  "Aperte ENTER (ou Ctrl+C) para ENCERRAR tudo... ")
        except EOFError:
            while True:
                time.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        encerrar(proc_tunel)
        encerrar(proc_api)
        print("\nAPI e tunel encerrados.")


if __name__ == "__main__":
    main()