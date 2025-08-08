import time
import os
import signal
import sys
from config import ChannelConfig
from monitor import TrafficMonitor
from server import PacketServer

def main():
    cfg = ChannelConfig.load_json('config.json')
    monitor = TrafficMonitor()

    enc = PacketServer(cfg.server_ip, cfg.encoder_port, cfg, monitor, role='encoder')
    dec = PacketServer(cfg.server_ip, cfg.decoder_port, cfg, monitor, role='decoder')

    enc.start()
    dec.start()

    stop = False
    def handler(sig, frame):
        nonlocal stop
        print('\n[MAIN] Ctrl+C received — shutting down...')
        stop = True

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    try:
        while not stop:
            time.sleep(0.2)
    finally:
        enc.stop()
        dec.stop()
        enc.join(timeout=2.0)
        dec.join(timeout=2.0)

        csv_path = monitor.save_csv(path=os.path.join('data','reports','logs.csv'))
        txt_path = monitor.save_report()
        png_path = monitor.plot_delay_chart(path=os.path.join('data','reports','delay_chart.png'))
        print('[MAIN] Saved:', csv_path, txt_path, png_path)
        print('[MAIN] Bye.')

if __name__ == '__main__':
    main()
