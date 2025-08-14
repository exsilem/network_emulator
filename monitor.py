import csv
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

class TrafficMonitor:
    def __init__(self):
        self.records = []

    def log_packet(self, packet_id, scheduled_ms, actual_ms,
                   transmission_ms, queued_ms, jitter_ms, propagation_ms,
                   lost=False):
        self.records.append({
            "packet_id": packet_id,
            "scheduled_ms": scheduled_ms,
            "actual_ms": actual_ms,
            "transmission_ms": transmission_ms,
            "queued_ms": queued_ms,
            "jitter_ms": jitter_ms,
            "propagation_ms": propagation_ms,
            "lost": bool(lost),
            "ts": datetime.utcnow().isoformat()
        })

    def save_csv(self, path=None):
        if path is None:
            path = os.path.join('data', 'reports', f'logs_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'ts','packet_id','scheduled_ms','actual_ms',
                'transmission_ms','queued_ms','jitter_ms','propagation_ms','lost'
            ])
            writer.writeheader()
            for r in self.records:
                writer.writerow(r)
        return path

    def save_report(self, path=None):
        if path is None:
            path = os.path.join('data', 'reports', f'report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.txt')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        total = len(self.records)
        delivered = [r for r in self.records if not r['lost']]
        lost_count = total - len(delivered)

        avg_scheduled = (sum(r['scheduled_ms'] for r in delivered) / len(delivered)) if delivered else 0
        avg_actual = (sum(r['actual_ms'] for r in delivered) / len(delivered)) if delivered else 0

        avg_transmission = (sum(r['transmission_ms'] for r in delivered) / len(delivered)) if delivered else 0
        avg_queued = (sum(r['queued_ms'] for r in delivered) / len(delivered)) if delivered else 0
        avg_jitter = (sum(r['jitter_ms'] for r in delivered) / len(delivered)) if delivered else 0
        avg_propagation = (sum(r['propagation_ms'] for r in delivered) / len(delivered)) if delivered else 0

        with open(path, 'w', encoding='utf-8') as f:
            f.write('Traffic emulator report\n')
            f.write('Generated: ' + datetime.utcnow().isoformat() + '\n\n')
            f.write(f'Total packets: {total}\n')
            f.write(f'Lost packets: {lost_count}\n')
            f.write(f'Average scheduled ms (delivered): {avg_scheduled:.3f}\n')
            f.write(f'Average actual ms (delivered): {avg_actual:.3f}\n\n')
            f.write('Average breakdown (ms) for delivered packets:\n')
            f.write(f'  transmission_ms: {avg_transmission:.3f}\n')
            f.write(f'  queued_ms:       {avg_queued:.3f}\n')
            f.write(f'  jitter_ms:       {avg_jitter:.3f}\n')
            f.write(f'  propagation_ms:  {avg_propagation:.3f}\n')
        return path

    def plot_delay_chart(self, path=None):
        if path is None:
            path = os.path.join('data', 'reports', f'delay_chart_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.png')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        delivered = [r for r in self.records if not r['lost']]
        if not delivered:
            return None
        xs = list(range(len(delivered)))
        scheduled = [r['scheduled_ms'] for r in delivered]
        actual = [r['actual_ms'] for r in delivered]
        plt.figure(figsize=(10,5))
        plt.plot(xs, scheduled, label='Scheduled delay (ms)', linestyle='--', marker='o')
        plt.plot(xs, actual, label='Actual delay (ms)', linestyle='-', marker='x')
        plt.xlabel('Packet index (delivered only)')
        plt.ylabel('Delay (ms)')
        plt.title('Scheduled vs Actual Delay')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(path, dpi=200)
        plt.close()
        return path