import socket
import threading
import time
import random

class PacketServer(threading.Thread):
    def __init__(self, ip, port, forward_ip, forward_port, config, monitor, role):
        super().__init__(daemon=True)
        self.ip = ip
        self.port = port
        self.forward_ip = forward_ip
        self.forward_port = forward_port
        self.config = config
        self.monitor = monitor
        self.role = role  # 'encoder' or 'decoder'
        self._running = threading.Event()
        self._running.set()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(1.0)

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
                self.monitor.log_packet(packet_id=packet, scheduled_ms=0.0, actual_ms=0.0, lost=True)
                continue

            # Задержка
            scheduled_ms = random.uniform(self.config.delay_min_ms, self.config.delay_max_ms)
            time.sleep(scheduled_ms / 1000.0)
            send_ts = time.time()
            actual_ms = (send_ts - recv_ts) * 1000.0

            # Логирование
            self.monitor.log_packet(packet_id=packet, scheduled_ms=scheduled_ms, actual_ms=actual_ms, lost=False)

            # Пересылка пакета
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