import logging
import os


class PacketMonitor:
    def __init__(self, config):
        self.config = config
        self.total_packets = 0
        self.lost_packets = 0

    def packet_processed(self):
        self.total_packets += 1

    def packet_lost(self):
        self.total_packets += 1
        self.lost_packets += 1

    def save_report(self):
        os.makedirs(os.path.dirname(self.config.report_path), exist_ok=True)

        with open(self.config.report_path, "w", encoding="utf-8") as f:
            f.write("=== Отчёт о передаче пакетов ===\n")
            f.write(f"Всего пакетов: {self.total_packets}\n")
            f.write(f"Потеряно пакетов: {self.lost_packets}\n")
            if self.total_packets > 0:
                loss_rate = (self.lost_packets / self.total_packets) * 100
                f.write(f"Процент потерь: {loss_rate:.2f}%\n")
            else:
                f.write("Нет переданных пакетов.\n")

        logging.info(f"Отчёт сохранён в {self.config.report_path}")