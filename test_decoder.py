import socket
import time

SERVER_IP = "127.0.0.1"
DECODER_PORT = 9999
NUM_PACKETS = 20
DELAY_BETWEEN_PACKETS = 0.2  # секунды

def send_packets():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"[TEST DECODER] Отправка {NUM_PACKETS} пакетов на порт {DECODER_PORT}")

    for i in range(NUM_PACKETS):
        packet = f"DEC_PKT_{i}".encode()
        sock.sendto(packet, (SERVER_IP, DECODER_PORT))
        print(f"[TEST DECODER] Отправлен пакет: {packet.decode()}")
        time.sleep(DELAY_BETWEEN_PACKETS)

    sock.close()
    print("[TEST DECODER] Тест завершён")

if __name__ == "__main__":
    send_packets()