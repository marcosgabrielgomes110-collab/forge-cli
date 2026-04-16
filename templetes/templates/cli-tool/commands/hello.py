"""Exemplo de comando - Hello World.

Para criar seu próprio comando:
1. Copie este arquivo
2. Altere o nome (ex: meu_comando.py)
3. Personalize a função add_subparser() e main()
"""

from utils.logger import get_logger

logger = get_logger(__name__)


def add_subparser(subparsers):
    """Registra o comando no parser principal.

    Args:
        subparsers: objeto subparsers do argparse
    """
    parser = subparsers.add_parser(
        "hello",
        help="Diz olá para alguém",
        description="Comando de exemplo que demonstra a estrutura"
    )
    parser.add_argument(
        "--name", "-n",
        default="Mundo",
        help="Nome para cumprimentar (padrão: Mundo)"
    )
    parser.add_argument(
        "--upper",
        action="store_true",
        help="Converter para maiúsculas"
    )
    parser.set_defaults(func=main)


def main(args):
    """Executa o comando.

    Args:
        args: argparse.Namespace com os argumentos
    """
    logger.info(f"Executando comando hello com name={args.name}")

    message = f"Olá, {args.name}!"
    if args.upper:
        message = message.upper()

    print(message)
    logger.debug(f"Mensagem exibida: {message}")
