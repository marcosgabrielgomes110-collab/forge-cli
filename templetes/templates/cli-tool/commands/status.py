"""Comando status - mostra informações do sistema.

Demonstra como acessar configurações e usar logging.
"""

import platform
from datetime import datetime

from utils.logger import get_logger
from utils.config import get_config

logger = get_logger(__name__)


def add_subparser(subparsers):
    """Registra o comando status."""
    parser = subparsers.add_parser(
        "status",
        help="Mostra status do sistema",
        description="Exibe informações sobre o ambiente"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Mostra informações detalhadas"
    )
    parser.set_defaults(func=main)


def main(args):
    """Executa o comando status."""
    logger.info("Verificando status do sistema...")

    config = get_config()

    print(f"Status: {datetime.now().isoformat()}")
    print(f"Log level: {config['log_level']}")

    if args.full:
        print(f"Python: {platform.python_version()}")
        print(f"Sistema: {platform.system()} {platform.release()}")
        print(f"Máquina: {platform.machine()}")

    logger.info("Status exibido com sucesso")
