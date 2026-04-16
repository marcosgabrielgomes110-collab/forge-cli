"""Configuração de logging com colorama e suporte a níveis."""

import logging
import sys
from pathlib import Path

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback caso colorama não esteja instalado
    class _DummyFore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = ""
    class _DummyStyle:
        RESET_ALL = BRIGHT = DIM = ""
    Fore = _DummyFore()
    Style = _DummyStyle()


# Cores por nível de log
LOG_COLORS = {
    logging.DEBUG: Fore.CYAN,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
}


class ColoredFormatter(logging.Formatter):
    """Formatter que adiciona cores aos logs no terminal."""

    def __init__(self, fmt=None, datefmt=None, use_colors=True):
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors and COLORAMA_AVAILABLE

    def format(self, record):
        if self.use_colors:
            color = LOG_COLORS.get(record.levelno, "")
            record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logging(level="INFO", log_file=None):
    """Configura o logging global.

    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Opcional - arquivo para salvar logs
    """
    handlers = []

    # Handler para console com cores
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    ))
    handlers.append(console_handler)

    # Handler para arquivo (sem cores)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        handlers.append(file_handler)

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        handlers=handlers,
        force=True,  # Sobrescreve configuração anterior
    )


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger configurado para o módulo."""
    return logging.getLogger(name)
