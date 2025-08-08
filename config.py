import json
from dataclasses import dataclass

@dataclass
class ChannelConfig:
    server_ip: str
    encoder_port: int
    decoder_port: int
    packet_loss: float
    delay_min_ms: float
    delay_max_ms: float

    @classmethod
    def load_json(cls, path: str = "config.json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            server_ip=data.get("server_ip", "127.0.0.1"),
            encoder_port=int(data.get("encoder_port", 8888)),
            decoder_port=int(data.get("decoder_port", 9999)),
            packet_loss=float(data.get("packet_loss", 0.0)),
            delay_min_ms=float(data.get("delay_min_ms", 50)),
            delay_max_ms=float(data.get("delay_max_ms", 150))
        )
