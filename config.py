import json
import os

class ChannelConfig:
    def __init__(self, cfg: dict):
        # сетевые параметры (старые поля)
        self.server_ip = cfg.get("server_ip", "127.0.0.1")
        self.encoder_port = cfg.get("encoder_port", 5001)
        self.decoder_port = cfg.get("decoder_port", 5002)

        # старые параметры задержек и потерь
        self.packet_loss = cfg.get("packet_loss", 0.0)
        self.delay_min_ms = cfg.get("delay_min_ms", 0.0)
        self.delay_max_ms = cfg.get("delay_max_ms", 0.0)

        # новые параметры для распределений задержек
        self.delay_distribution_type = cfg.get("delay_distribution_type", "uniform")
        self.delay_param1 = cfg.get("delay_param1", None)  # alpha или mu
        self.delay_param2 = cfg.get("delay_param2", None)  # beta или sigma
        self.delay_distribution_file = cfg.get("delay_distribution_file", None)

        # параметры джиттера
        self.jitter_distribution_type = cfg.get("jitter_distribution_type", "normal")
        self.jitter_mu_ms = cfg.get("jitter_mu_ms", 0.0)
        self.jitter_sigma_ms = cfg.get("jitter_sigma_ms", 0.0)
        self.jitter_distribution_file = cfg.get("jitter_distribution_file", None)

        # параметры канала
        self.bandwidth_bps = cfg.get("bandwidth_bps", 10_000_000)  # 10 Mbps по умолчанию
        self.bandwidth_distribution_file = cfg.get("bandwidth_distribution_file", None)

    @classmethod
    def load_json(cls, path="config.json"):
        """Загружает конфиг из JSON и возвращает ChannelConfig"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return cls(cfg)