import logging
from config import ChannelConfig
from server import PacketServer
from monitor import PacketMonitor


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )

    config = ChannelConfig.load("config.json")

    monitor = PacketMonitor(config)
    server = PacketServer(config, monitor)

    try:
        logging.info("Запуск сервера. Нажмите Ctrl+C для остановки.")
        server.start()
        while server.is_alive():
            server.join(timeout=1)
    except KeyboardInterrupt:
        logging.info("Остановка сервера по Ctrl+C...")
        server.stop()
        server.join()
    finally:
        monitor.save_report()
        logging.info("Работа завершена.")


if __name__ == "__main__":
    main()