import json
import os
import numpy as np
from scipy.stats import beta, norm


class ChannelConfig:
    def __init__(
        self,
        encoder_addr=('127.0.0.1', 8888),
        decoder_addr=('127.0.0.1', 9999),
        encoder_port=8888,
        decoder_port=9999,
        latency_alpha=2.0,
        latency_beta=5.0,
        jitter_mu=0.0,
        jitter_sigma=1.5,
        loss_rate=0.05,
        bandwidth=None
    ):
        self.encoder_addr = tuple(encoder_addr)
        self.decoder_addr = tuple(decoder_addr)
        self.encoder_port = encoder_port
        self.decoder_port = decoder_port
        self.latency_alpha = latency_alpha
        self.latency_beta = latency_beta
        self.jitter_mu = jitter_mu
        self.jitter_sigma = jitter_sigma
        self.loss_rate = loss_rate
        self.bandwidth = bandwidth

        self.validate()
        self.update_distributions()

    def validate(self):
        assert 0 <= self.loss_rate <= 1, "Loss rate must be between 0 and 1"
        assert self.encoder_port > 0 and self.decoder_port > 0, "Ports must be positive integers"
        assert self.latency_alpha > 0 and self.latency_beta > 0, "Beta distribution parameters must be > 0"
        assert self.jitter_sigma >= 0, "Jitter sigma must be >= 0"
        if self.bandwidth is not None:
            assert self.bandwidth > 0, "Bandwidth must be positive or None"

    def update_distributions(self):
        self.latency_dist = beta(self.latency_alpha, self.latency_beta)
        self.jitter_dist = norm(self.jitter_mu, self.jitter_sigma)

    def generate_latency(self):
        """Сгенерировать задержку в мс (0-100)"""
        return self.latency_dist.rvs() * 100

    def generate_jitter(self):
        """Сгенерировать джиттер в мс"""
        return self.jitter_dist.rvs()

    def should_drop_packet(self):
        """Вероятность потери пакета"""
        return np.random.random() < self.loss_rate

    def to_dict(self):
        return {
            "encoder_addr": self.encoder_addr,
            "decoder_addr": self.decoder_addr,
            "encoder_port": self.encoder_port,
            "decoder_port": self.decoder_port,
            "latency_alpha": self.latency_alpha,
            "latency_beta": self.latency_beta,
            "jitter_mu": self.jitter_mu,
            "jitter_sigma": self.jitter_sigma,
            "loss_rate": self.loss_rate,
            "bandwidth": self.bandwidth,
        }

    def to_json(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_config(cls, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Config file '{filepath}' not found.")
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls(**data)

    def __str__(self):
        return (f"ChannelConfig("
                f"encoder={self.encoder_addr}, decoder={self.decoder_addr}, "
                f"latency=Beta(α={self.latency_alpha}, β={self.latency_beta}), "
                f"jitter=Norm(μ={self.jitter_mu}, σ={self.jitter_sigma}), "
                f"loss={self.loss_rate*100:.1f}%, "
                f"bandwidth={self.bandwidth or 'unlimited'})")


# Внешняя функция для main.py
def load_config(filepath='config.json'):
    return ChannelConfig.load_config(filepath)