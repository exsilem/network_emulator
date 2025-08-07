import csv
import os
import time
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

class MonitoringSystem:
    def __init__(self):
        self.logs_path = os.path.join("data", "logs.csv")
        self.reports_path = os.path.join("data", "reports")
        os.makedirs(os.path.dirname(self.logs_path), exist_ok=True)
        os.makedirs(self.reports_path, exist_ok=True)

        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(self.logs_path):
            with open(self.logs_path, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "packet_id",
                    "dropped",
                    "delay_ms",
                    "intended_delay_ms",
                    "size_bytes"
                ])

    def log_packet(self, packet_id, dropped, delay_ms=0, intended_delay_ms=0, size_bytes=0):
        with open(self.logs_path, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.utcnow().isoformat(),
                packet_id,
                int(dropped),
                round(delay_ms, 2),
                round(intended_delay_ms, 2),
                size_bytes
            ])

    def generate_report(self):
        if not os.path.exists(self.logs_path):
            print("No logs found.")
            return

        df = pd.read_csv(self.logs_path)

        if df.empty:
            print("No data to generate report.")
            return

        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_base = os.path.join(self.reports_path, f"report_{timestamp_str}")

        # Статистика
        total = len(df)
        dropped = df["dropped"].sum()
        delivered = total - dropped
        avg_delay = df[df["dropped"] == 0]["delay_ms"].mean()

        stats_text = (
            f"Total packets: {total}\n"
            f"Dropped packets: {dropped} ({dropped / total:.2%})\n"
            f"Delivered packets: {delivered} ({delivered / total:.2%})\n"
            f"Average delay (ms): {avg_delay:.2f}\n"
        )

        # Сохраняем статистику в txt
        with open(report_base + "_stats.txt", "w") as f:
            f.write(stats_text)

        # График задержек
        plt.figure(figsize=(10, 5))
        df_delivered = df[df["dropped"] == 0]
        plt.plot(df_delivered["delay_ms"].values, label="Actual Delay (ms)")
        plt.plot(df_delivered["intended_delay_ms"].values, label="Intended Delay (ms)", linestyle="--")
        plt.title("Packet Delays")
        plt.xlabel("Packet Index")
        plt.ylabel("Delay (ms)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(report_base + "_delay_plot.png")
        plt.close()

        print(f"Report saved to: {report_base}_*.txt/.png")