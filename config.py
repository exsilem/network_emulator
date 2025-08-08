import json
import logging
from dataclasses import dataclass
from typing import Tuple


@dataclass
class ChannelConfig:
    encoder_port: int
    decoder_port: int
    loss_probability: float
    delay_range: Tuple[float, float]
    report_path: str

    @staticmethod
    def load(file_path: str) -> "ChannelConfig":
        """
        Загружает конфигурацию из JSON-файла.
        При ошибках — логирует их и выбрасывает исключение.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            logging.info(f"Конфигурация загружена из {file_path}")

            return ChannelConfig(
                encoder_port=data.get("encoder_port", 8888),
                decoder_port=data.get("decoder_port", 9999),
                loss_probability=data.get("loss_probability", 0.1),
                delay_range=tuple(data.get("delay_range", [0.01, 0.05])),
                report_path=data.get("report_path", "data/reports/report.txt")
            )

        except FileNotFoundError:
            logging.error(f"Файл конфигурации {file_path} не найден")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"Ошибка разбора JSON в {file_path}: {e}")
            raise
        except Exception as e:
            logging.error(f"Неожиданная ошибка при загрузке конфигурации: {e}")
            raise