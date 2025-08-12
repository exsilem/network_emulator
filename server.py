import socket
import threading
import time
import random
import math
import csv
import os

class PacketServer(threading.Thread):
    def __init__(self, ip, port, config, monitor, role):
        super().__init__(daemon=True)
        self.ip = ip
        self.port = port
        self.config = config
        self.monitor = monitor
        self.role = role  # 'encoder' or 'decoder' label
        self._running = threading.Event()
        self._running.set()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(1.0)

        # очередь передачи (для моделирования пропускной способности)
        self.next_free_time = time.time()

        # загрузка выборок из файла (если заданы)
        self.delay_samples = self._load_distribution(getattr(config, "delay_distribution_file", None))
        self.jitter_samples = self._load_distribution(getattr(config, "jitter_distribution_file", None))
        self.bandwidth_samples = self._load_distribution(getattr(config, "bandwidth_distribution_file", None))

    def _load_distribution(self, path):
        """Загружает распределение из CSV (один столбец чисел)"""
        if not path or not os.path.exists(path):
            return None
        values = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        values.append(float(row[0]))
                    except (ValueError, IndexError):
                        continue
        except Exception:
            return None
        return values if values else None

    def _sample_distribution(self, dist_type, param1=None, param2=None, samples=None, min_val=None, max_val=None):
        """Выбирает значение из распределения"""
        if samples:
            return random.choice(samples)
        if dist_type == "beta" and param1 and param2:
            # betavariate возвращает от 0 до 1 — масштабируем
            base = random.betavariate(param1, param2)
            if min_val is not None and max_val is not None:
                return min_val + base * (max_val - min_val)
            return base
        elif dist_type == "normal" and param1 is not None and param2 is not None:
            # param1 = mu, param2 = sigma
            return max(0.0, random.gauss(param1, param2))
        else:
            # default uniform
            if min_val is not None and max_val is not None:
                return random.uniform(min_val, max_val)
            return 0.0

    def run(self):
        print(f'[SERVER-{self.role}] Listening on {self.ip}:{self.port}')
        while self._running.is_set():
            try:
                data, addr = self.sock.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                break

            recv_ts = time.time()
            packet = data.decode(errors='ignore')
            packet_size_bytes = len(data)

            # decide drop
            if random.random() < self.config.packet_loss:
                self.monitor.log_packet(
                    packet_id=packet,
                    scheduled_ms=scheduled_ms,
                    actual_ms=actual_ms,
                    lost=False,
                    propagation_ms=propagation_ms,
                    jitter_ms=jitter_ms,
                    transmission_ms=transmission_ms,
                    queued_ms=queued_ms
                )
                continue

            # задержка распространения (propagation delay)
            propagation_ms = self._sample_distribution(
                getattr(self.config, "delay_distribution_type", "uniform"),
                getattr(self.config, "delay_param1", None),
                getattr(self.config, "delay_param2", None),
                samples=self.delay_samples,
                min_val=self.config.delay_min_ms,
                max_val=self.config.delay_max_ms
            )

            # джиттер
            jitter_ms = self._sample_distribution(
                getattr(self.config, "jitter_distribution_type", "normal"),
                getattr(self.config, "jitter_mu_ms", 0.0),
                getattr(self.config, "jitter_sigma_ms", 0.0),
                samples=self.jitter_samples
            )

            # пропускная способность (bps)
            if self.bandwidth_samples:
                bandwidth_bps = random.choice(self.bandwidth_samples)
            else:
                bandwidth_bps = getattr(self.config, "bandwidth_bps", 10_000_000)  # 10 Mbps по умолчанию

            transmission_ms = (packet_size_bytes * 8) / max(bandwidth_bps, 1) * 1000.0

            # моделирование очереди
            queued_ms = 0.0
            now = time.time()
            if now < self.next_free_time:
                queued_ms = (self.next_free_time - now) * 1000.0
                self.next_free_time += transmission_ms / 1000.0
            else:
                self.next_free_time = now + transmission_ms / 1000.0

            # итоговая запланированная задержка
            scheduled_ms = propagation_ms + jitter_ms + transmission_ms + queued_ms

            # симуляция задержки
            time.sleep(scheduled_ms / 1000.0)
            send_ts = time.time()
            actual_ms = (send_ts - recv_ts) * 1000.0

            self.monitor.log_packet(
                packet_id=packet,
                scheduled_ms=scheduled_ms,
                actual_ms=actual_ms,
                lost=False
            )

        self.sock.close()

    def stop(self):
        self._running.clear()
        try:
            self.sock.close()
        except Exception:
            pass