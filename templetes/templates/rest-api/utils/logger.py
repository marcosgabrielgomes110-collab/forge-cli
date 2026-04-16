"""Configuração de logging estruturado."""

import logging
import sys
from pathlib import Path

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    class _Dummy:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = ""
        RESET_ALL = BRIGHT = DIM = ""
    Fore = _Dummy()
    Style = _Dummy()


LOG_COLORS = {
    logging.DEBUG: Fore.CYAN,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
}


class ColoredFormatter(logging.Formatter):
    """Formatter colorido para terminal."""

    def __init__(self, fmt=None, use_colors=True):
        super().__init__(fmt)
        self.use_colors = use_colors and COLORAMA_AVAILABLE

    def format(self, record):
        if self.use_colors:
            color = LOG_COLORS.get(record.levelno, "")
            record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logging(level="INFO", log_file=None):
    """Configura logging global."""
    handlers = []

    # Console com cores
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(ColoredFormatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    ))
    handlers.append(console)

    # Arquivo (sem cores)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        handlers.append(fh)

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        handlers=handlers,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Retorna logger configurado."""
    return logging.getLogger(name)
