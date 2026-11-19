from wifi import conectar_wifi
from teclado import executar_validador

print("================================")
print("       VALIDADOR DE SENHAS")
print("================================")

wifi = conectar_wifi()

if wifi:
    executar_validador()
else:
    print("Sistema iniciado sem conexao.")
