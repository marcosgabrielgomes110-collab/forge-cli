#!/usr/bin/env python3
"""{{project_name}} - CLI Tool Modular

Estrutura:
  commands/     - Coloque seus comandos aqui (um arquivo = um comando)
  utils/        - Utilitários (logging, config, etc)
  main.py       - Entry point (não precisa editar)

Para adicionar um comando:
  1. Crie um arquivo em commands/<nome>.py
  2. Defina uma função main(args) que recebe argparse.Namespace
  3. Pronto! O comando será registrado automaticamente.

Exemplo em commands/hello.py:
  def main(args):
      print(f"Olá, {args.name}!")

  def add_subparser(subparsers):
      parser = subparsers.add_parser("hello", help="Diz olá")
      parser.add_argument("--name", default="Mundo")
"""

import argparse
import importlib
import sys
from pathlib import Path

from utils.logger import get_logger, setup_logging
from utils.config import get_config

logger = get_logger(__name__)


def discover_commands():
    """Descobre automaticamente todos os comandos em commands/."""
    commands_dir = Path(__file__).parent / "commands"
    commands = {}

    if not commands_dir.exists():
        logger.warning(f"Diretório commands/ não encontrado: {commands_dir}")
        return commands

    for file in commands_dir.glob("*.py"):
        if file.name.startswith("_"):
            continue
        module_name = file.stem
        try:
            module = importlib.import_module(f"commands.{module_name}")
            commands[module_name] = module
            logger.debug(f"Comando carregado: {module_name}")
        except Exception as e:
            logger.error(f"Erro ao carregar comando {module_name}: {e}")

    return commands


def main():
    # Setup logging antes de tudo
    config = get_config()
    setup_logging(config.get("log_level", "INFO"))

    parser = argparse.ArgumentParser(
        description="{{project_name}} - CLI Tool Modular",
        prog="{{project_name}}",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Modo verbose (debug logging)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # Descobre e registra comandos automaticamente
    commands = discover_commands()

    for name, module in commands.items():
        if hasattr(module, "add_subparser"):
            module.add_subparser(subparsers)
        else:
            # Registro automático básico
            sub = subparsers.add_parser(name, help=f"Comando {name}")
            sub.set_defaults(func=module.main if hasattr(module, "main") else lambda args: print(f"Comando {name} não implementado"))

    args = parser.parse_args()

    # Ajusta log level se verbose
    if args.verbose:
        setup_logging("DEBUG")

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Executa o comando
    if hasattr(args, "func"):
        try:
            args.func(args)
        except Exception as e:
            logger.error(f"Erro ao executar comando: {e}")
            sys.exit(1)
    else:
        logger.error(f"Comando '{args.command}' não implementado corretamente")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
