import socket, time
cfg = {
    'server_ip': '127.0.0.1',
    'decoder_port': 5002,  # <-- ДОЛЖЕН совпадать с config.json
    'num': 20,
    'interval': 0.12
}
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for i in range(cfg['num']):
        pkt = f'DEC_PKT_{i}'.encode()
        s.sendto(pkt, (cfg['server_ip'], cfg['decoder_port']))
        time.sleep(cfg['interval'])
    s.close()
if __name__=='__main__': main()