import socket
import threading
import logging
import random
import time


class PacketServer(threading.Thread):
    def __init__(self, config, monitor):
        super().__init__(daemon=True)
        self.config = config
        self.monitor = monitor
        self.running = threading.Event()
        self.running.set()

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", self.config.encoder_port))
        sock.settimeout(1.0)  # <<< ВАЖНО: ставим таймаут один раз

        logging.info(f"Сервер слушает порт {self.config.encoder_port}")

        while self.running.is_set():
            try:
                data, addr = sock.recvfrom(1024)
            except socket.timeout:
                continue
            except OSError:
                break
            except Exception as e:
                logging.error(f"Ошибка при приёме данных: {e}")
                break

            packet = data.decode()
            logging.info(f"Получен пакет от {addr}: {packet}")

            if random.random() < self.config.loss_probability:
                logging.warning("Пакет потерян")
                self.monitor.packet_lost()
                continue

            delay = random.uniform(*self.config.delay_range)
            time.sleep(delay)

            self.monitor.packet_processed()

        sock.close()

    def stop(self):
        self.running.clear()