import socket, time
cfg = {
    'server_ip': '127.0.0.1',
    'encoder_port': 8888,
    'num': 20,
    'interval': 0.1
}
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for i in range(cfg['num']):
        pkt = f'ENC_PKT_{i}'.encode()
        s.sendto(pkt, (cfg['server_ip'], cfg['encoder_port']))
        time.sleep(cfg['interval'])
    s.close()
if __name__=='__main__': main()
