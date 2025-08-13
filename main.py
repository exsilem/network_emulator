import time
from config import ChannelConfig
from monitor import TrafficMonitor
from server import PacketServer

def main():
    cfg = ChannelConfig.load_json('config.json')
    monitor = TrafficMonitor()

    # Encoder → Decoder
    enc = PacketServer(
        cfg.server_ip,
        cfg.encoder_port,
        cfg.server_ip,
        cfg.decoder_port,
        cfg,
        monitor,
        role='encoder'
    )

    # Decoder → Encoder
    dec = PacketServer(
        cfg.server_ip,
        cfg.decoder_port,
        cfg.server_ip,
        cfg.encoder_port,
        cfg,
        monitor,
        role='decoder'
    )

    enc.start()
    dec.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[MAIN] Stopping servers...")
        enc.stop()
        dec.stop()
        enc.join()
        dec.join()
        print("[MAIN] Saving reports...")
        monitor.save_csv()
        monitor.save_report()
        monitor.plot_delay_chart()
        print("[MAIN] Done. Reports are in data/reports/")

if __name__ == '__main__':
    main()