import socket
import threading
import time
import random
import os
import csv
from itertools import cycle

class PacketServer(threading.Thread):
    def __init__(self, ip, port, forward_ip, forward_port, config, monitor, role):
        super().__init__(daemon=True)
        self.ip = ip
        self.port = port
        self.forward_ip = forward_ip
        self.forward_port = forward_port
        self.config = config
        self.monitor = monitor
        self.role = role
        self._running = threading.Event()
        self._running.set()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(1.0)

        # Загружаем распределения из CSV, если есть
        self.delays_iter = self._load_csv_iter("data/distributions/delays.csv")
        self.jitter_iter = self._load_csv_iter("data/distributions/jitter.csv")
        self.bandwidth_iter = self._load_csv_iter("data/distributions/bandwidth.csv")

    def _load_csv_iter(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    values = [float(row[0]) for row in reader if row]
                if values:
                    print(f"[SERVER-{self.role}] Loaded distribution from {path} ({len(values)} values)")
                    return cycle(values)  # бесконечный цикл по значениям
            except Exception as e:
                print(f"[SERVER-{self.role}] Failed to load {path}: {e}")
        return None

    def run(self):
        print(f'[SERVER-{self.role}] Listening on {self.ip}:{self.port}, forwarding to {self.forward_ip}:{self.forward_port}')
        while self._running.is_set():
            try:
                data, addr = self.sock.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                break
            recv_ts = time.time()
            packet = data.decode(errors='ignore')

            # Потеря пакета
            if random.random() < getattr(self.config, 'packet_loss', 0.0):
                self.monitor.log_packet(packet_id=packet, scheduled_ms=0.0, actual_ms=0.0,
                                        transmission_ms=0.0, queued_ms=0.0,
                                        jitter_ms=0.0, propagation_ms=0.0,
                                        lost=True)
                continue

            # --- Моделирование задержки ---
            packet_bits = len(data) * 8

            # Пропускная способность (bps)
            if self.bandwidth_iter:
                bandwidth_bps = max(1.0, next(self.bandwidth_iter))
            else:
                bandwidth_bps = getattr(self.config, 'bandwidth_bps', 1_000_000)

            transmission_ms = (packet_bits / bandwidth_bps) * 1000.0

            # Очередь
            if self.delays_iter:
                queued_ms = next(self.delays_iter)
            else:
                queued_ms = random.uniform(self.config.delay_min_ms, self.config.delay_max_ms)

            # Джиттер
            if self.jitter_iter:
                jitter_ms = next(self.jitter_iter)
            else:
                jitter_ms = max(0.0, random.gauss(5.0, 2.0))

            # Задержка распространения
            propagation_ms = getattr(self.config, 'propagation_ms', 250.0)

            scheduled_ms = transmission_ms + queued_ms + jitter_ms + propagation_ms

            time.sleep(scheduled_ms / 1000.0)
            send_ts = time.time()
            actual_ms = (send_ts - recv_ts) * 1000.0

            self.monitor.log_packet(packet_id=packet,
                                    scheduled_ms=scheduled_ms,
                                    actual_ms=actual_ms,
                                    transmission_ms=transmission_ms,
                                    queued_ms=queued_ms,
                                    jitter_ms=jitter_ms,
                                    propagation_ms=propagation_ms,
                                    lost=False)

            try:
                self.sock.sendto(data, (self.forward_ip, self.forward_port))
            except Exception as e:
                print(f"[SERVER-{self.role}] Forward error: {e}")

        self.sock.close()

    def stop(self):
        self._running.clear()
        try:
            self.sock.close()
        except Exception:
            pass