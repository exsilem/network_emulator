import socket
import time

SERVER_IP = "127.0.0.1"
ENCODER_PORT = 8888
DECODER_PORT = 9999
NUM_PACKETS = 20
DELAY_BETWEEN_PACKETS = 0.2  # секунды
TIMEOUT = 2.0  # максимум времени ожидания ответа

def send_and_receive():
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind((SERVER_IP, DECODER_PORT))
    recv_sock.settimeout(TIMEOUT)

    print(f"[TEST ENCODER] Отправка {NUM_PACKETS} пакетов на порт {ENCODER_PORT}")

    for i in range(NUM_PACKETS):
        packet_data = f"ENC_PKT_{i}"
        send_time = time.time()

        # Отправляем пакет
        send_sock.sendto(packet_data.encode(), (SERVER_IP, ENCODER_PORT))
        print(f"[TEST ENCODER] Отправлен: {packet_data}")

        try:
            data, _ = recv_sock.recvfrom(1024)
            receive_time = time.time()
            delay = (receive_time - send_time) * 1000  # в мс
            print(f"[TEST ENCODER] Получен ответ: {data.decode()} | Задержка: {delay:.2f} мс")
        except socket.timeout:
            print(f"[TEST ENCODER] Потеря пакета: {packet_data}")

        time.sleep(DELAY_BETWEEN_PACKETS)

    send_sock.close()
    recv_sock.close()
    print("[TEST ENCODER] Тест завершён")

if __name__ == "__main__":
    send_and_receive()