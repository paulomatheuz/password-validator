import network
from time import sleep

def conectar_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    wifi.connect("Wokwi-GUEST", "")

    tentativas = 0

    while not wifi.isconnected() and tentativas < 15:
        print("Conectando ao Wi-Fi...")
        sleep(1)
        tentativas += 1

    if wifi.isconnected():
        print("Wi-Fi conectado!")
        print("IP:", wifi.ifconfig()[0])
        return True
    else:
        print("Falha ao conectar ao Wi-Fi.")
        return False