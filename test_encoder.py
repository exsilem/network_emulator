import socket
import time
import struct
import os
import random

FRAG_HEADER_SIZE = 8  # 4 байта packet_id, 2 байта fragment_index, 2 байта total_fragments
MAX_PAYLOAD_SIZE = 1200  # полезная нагрузка в одном фрагменте
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5001

def generate_large_packet(size_bytes):
    """Генерируем случайный пакет данных заданного размера."""
    return os.urandom(size_bytes)

def send_large_packet(sock, packet_id, payload):
    """Разбиваем пакет на фрагменты и отправляем их с заголовками."""
    total_frags = (len(payload) + MAX_PAYLOAD_SIZE - 1) // MAX_PAYLOAD_SIZE
    for frag_idx in range(total_frags):
        frag_payload = payload[frag_idx * MAX_PAYLOAD_SIZE:(frag_idx + 1) * MAX_PAYLOAD_SIZE]
        header = struct.pack("!IHH", packet_id, frag_idx, total_frags)
        sock.sendto(header + frag_payload, (SERVER_IP, SERVER_PORT))

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet_id = 0

    num_packets = 5  # количество больших пакетов
    packet_size_bytes = 5000  # размер одного пакета (5 KB для теста, можно больше)
    interval = 0.5  # интервал между пакетами

    for _ in range(num_packets):
        payload = generate_large_packet(packet_size_bytes)
        send_large_packet(sock, packet_id, payload)
        print(f"[TEST_ENCODER] Sent packet_id={packet_id}, size={len(payload)} bytes")
        packet_id += 1
        time.sleep(interval)

    sock.close()

if __name__ == "__main__":
    main()