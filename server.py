import socket
import threading
import time
import random
import logging
from queue import Queue
from monitor import MonitoringSystem
from config import ChannelConfig

# Очередь пакетов от энкодера
packet_queue = Queue()

# Мониторинг
monitor = MonitoringSystem()


def apply_jitter_and_delay(config: ChannelConfig):
    """Добавить задержку и джиттер"""
    delay_ms = config.generate_latency() + config.generate_jitter()
    delay_ms = max(0, delay_ms)  # Без отрицательных значений
    delay = delay_ms / 1000
    time.sleep(delay)
    return delay_ms


def handle_encoder_connection(conn, addr, config: ChannelConfig):
    logging.info(f"[ENCODER] Подключение от {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            packet_id = data.decode().strip()
            timestamp_received = time.time()

            # Потеря пакета
            if config.should_drop_packet():
                logging.info(f"[ENCODER] Потерян пакет: {packet_id}")
                monitor.log_packet(packet_id, dropped=True)
                continue

            # Добавить в очередь
            packet_queue.put((packet_id, timestamp_received, data))
            logging.info(f"[ENCODER] Пакет в очереди: {packet_id}")

    except Exception as e:
        logging.error(f"[ENCODER] Ошибка: {e}")
    finally:
        conn.close()
        logging.info("[ENCODER] Отключение")


def handle_decoder_connection(conn, addr, config: ChannelConfig):
    logging.info(f"[DECODER] Подключение от {addr}")
    try:
        while True:
            if not packet_queue.empty():
                packet_id, timestamp_received, data = packet_queue.get()

                delay_ms = apply_jitter_and_delay(config)
                timestamp_sent = time.time()

                # Пропускная способность
                if config.bandwidth:
                    size = len(data)
                    time.sleep(size * 8 / config.bandwidth)  # bits / bps

                conn.sendall(data)
                logging.info(f"[DECODER] Отправлен пакет: {packet_id}")

                monitor.log_packet(
                    packet_id,
                    dropped=False,
                    delay_ms=(timestamp_sent - timestamp_received) * 1000,
                    intended_delay_ms=delay_ms,
                    size_bytes=len(data),
                )
            else:
                time.sleep(0.01)

    except Exception as e:
        logging.error(f"[DECODER] Ошибка: {e}")
    finally:
        conn.close()
        logging.info("[DECODER] Отключение")


def start_server(config: ChannelConfig):
    encoder_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    decoder_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    encoder_socket.bind(("localhost", config.encoder_port))
    decoder_socket.bind(("localhost", config.decoder_port))

    encoder_socket.listen(5)
    decoder_socket.listen(5)

    logging.info(f"[SERVER] Encoder слушает на порту {config.encoder_port}")
    logging.info(f"[SERVER] Decoder слушает на порту {config.decoder_port}")

    try:
        while True:
            enc_conn, enc_addr = encoder_socket.accept()
            dec_conn, dec_addr = decoder_socket.accept()

            threading.Thread(
                target=handle_encoder_connection,
                args=(enc_conn, enc_addr, config),
                daemon=True
            ).start()

            threading.Thread(
                target=handle_decoder_connection,
                args=(dec_conn, dec_addr, config),
                daemon=True
            ).start()

    except KeyboardInterrupt:
        logging.info("[SERVER] Остановка сервера по Ctrl+C")

    finally:
        encoder_socket.close()
        decoder_socket.close()
        monitor.generate_report()
        logging.info("[SERVER] Сервер завершил работу")