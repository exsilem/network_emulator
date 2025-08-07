import logging
import threading
import signal
import sys
import time

from config import load_config
from server import start_server
from monitor import MonitoringSystem

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - NetworkEmulator - %(levelname)s - %(message)s",
)

# Глобальные переменные
monitor = MonitoringSystem()
running = True
processed_packets = 0

def shutdown_handler(sig, frame):
    global running
    logging.info("Server shutdown initiated...")
    running = False

signal.signal(signal.SIGINT, shutdown_handler)

def encoder_handler(data, delay_ms):
    global processed_packets
    packet_id = data.decode()
    size_bytes = len(data)
    time.sleep(delay_ms / 1000.0)
    monitor.log_packet(packet_id=packet_id, dropped=False, delay_ms=delay_ms, intended_delay_ms=delay_ms, size_bytes=size_bytes)
    logging.info(f"Received from encoder: {packet_id}")
    processed_packets += 1

def decoder_handler(data, delay_ms):
    packet_id = data.decode()
    size_bytes = len(data)
    time.sleep(delay_ms / 1000.0)
    monitor.log_packet(packet_id=packet_id, dropped=False, delay_ms=delay_ms, intended_delay_ms=delay_ms, size_bytes=size_bytes)
    logging.info(f"Received from decoder: {packet_id}")

def main():
    global processed_packets

    config = load_config()

    encoder_port = config.encoder_port
    decoder_port = config.decoder_port
    delay_ms = config.latency_dist

    # Запуск серверов
    server_thread = threading.Thread(target=start_server, args=(config,), daemon=True)
    server_thread.start()
    logging.info(f"Server started with encoder port {config.encoder_port} and decoder port {config.decoder_port}")

    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown_handler(None, None)

    if processed_packets == 0:
        logging.info("No packets processed, report not generated")
    else:
        monitor.generate_report()

    logging.info("Server shutdown complete")

if __name__ == "__main__":
    main()