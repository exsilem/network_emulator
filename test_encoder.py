import socket
import time

SERVER_IP = "127.0.0.1"
ENCODER_PORT = 8888
NUM_PACKETS = 20
DELAY_BETWEEN_PACKETS = 0.2  # секунды


def send_packets():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"[TEST ENCODER] Отправка {NUM_PACKETS} пакетов на порт {ENCODER_PORT}")

    for i in range(NUM_PACKETS):
        packet = f"ENC_PKT_{i}".encode()
        sock.sendto(packet, (SERVER_IP, ENCODER_PORT))
        print(f"[TEST ENCODER] Отправлен пакет: {packet.decode()}")
        time.sleep(DELAY_BETWEEN_PACKETS)

    sock.close()
    print("[TEST ENCODER] Тест завершён")


if __name__ == "__main__":
    send_packets()