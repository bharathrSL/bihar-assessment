"""Structured file and console logging."""
import logging
from pathlib import Path

def get_logger(name: str, log_dir: str | Path | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers: return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    console = logging.StreamHandler(); console.setFormatter(formatter); logger.addHandler(console)
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(Path(log_dir) / "processing.log", encoding="utf-8")
        handler.setFormatter(formatter); logger.addHandler(handler)
    return logger
