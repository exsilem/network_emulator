import csv
import os
import matplotlib
matplotlib.use('Agg')  # headless backend for PNG
import matplotlib.pyplot as plt
from datetime import datetime

class TrafficMonitor:
    def __init__(self):
        # records: list of dicts with keys: packet_id, scheduled_ms, actual_ms, lost (bool), ts, optional components
        self.records = []

    def log_packet(self, packet_id, scheduled_ms, actual_ms, lost=False,
                   propagation_ms=None, jitter_ms=None, transmission_ms=None, queued_ms=None):
        self.records.append({
            "packet_id": packet_id,
            "scheduled_ms": scheduled_ms,
            "actual_ms": actual_ms,
            "lost": bool(lost),
            "propagation_ms": propagation_ms,
            "jitter_ms": jitter_ms,
            "transmission_ms": transmission_ms,
            "queued_ms": queued_ms,
            "ts": datetime.utcnow().isoformat()
        })

    def save_csv(self, path=None):
        if path is None:
            path = os.path.join('data', 'reports', 'logs_' + datetime.utcnow().strftime('%Y%m%d_%H%M%S') + '.csv')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fieldnames = ['ts','packet_id','scheduled_ms','actual_ms','lost',
                      'propagation_ms','jitter_ms','transmission_ms','queued_ms']
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in self.records:
                # ensure all fields present
                out = {k: r.get(k, '') for k in fieldnames}
                writer.writerow(out)
        return path

    def save_report(self, path=None):
        if path is None:
            path = os.path.join('data', 'reports', 'report_' + datetime.utcnow().strftime('%Y%m%d_%H%M%S') + '.txt')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        total = len(self.records)
        lost = sum(1 for r in self.records if r['lost'])
        delivered = [r for r in self.records if not r['lost']]
        avg_scheduled = (sum(r['scheduled_ms'] for r in delivered) / max(1, len(delivered))) if delivered else 0.0
        avg_actual = (sum(r['actual_ms'] for r in delivered) / max(1, len(delivered))) if delivered else 0.0
        # breakdown averages
        avg_trans = (sum(r.get('transmission_ms') or 0.0 for r in delivered) / max(1, len(delivered))) if delivered else 0.0
        avg_queue = (sum(r.get('queued_ms') or 0.0 for r in delivered) / max(1, len(delivered))) if delivered else 0.0
        avg_jitter = (sum(r.get('jitter_ms') or 0.0 for r in delivered) / max(1, len(delivered))) if delivered else 0.0
        avg_prop = (sum(r.get('propagation_ms') or 0.0 for r in delivered) / max(1, len(delivered))) if delivered else 0.0

        with open(path, 'w', encoding='utf-8') as f:
            f.write('Traffic emulator report\n')
            f.write('Generated: ' + datetime.utcnow().isoformat() + '\n\n')
            f.write(f'Total packets: {total}\n')
            f.write(f'Lost packets: {lost}\n')
            f.write(f'Average scheduled ms (delivered): {avg_scheduled:.3f}\n')
            f.write(f'Average actual ms (delivered): {avg_actual:.3f}\n\n')
            f.write('Average breakdown (ms) for delivered packets:\n')
            f.write(f'  transmission_ms: {avg_trans:.3f}\n')
            f.write(f'  queued_ms:       {avg_queue:.3f}\n')
            f.write(f'  jitter_ms:       {avg_jitter:.3f}\n')
            f.write(f'  propagation_ms:  {avg_prop:.3f}\n')
        return path

    def plot_delay_chart(self, path=None):
        if path is None:
            path = os.path.join('data', 'reports', 'delay_chart_' + datetime.utcnow().strftime('%Y%m%d_%H%M%S') + '.png')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # use only delivered packets for plotting
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
