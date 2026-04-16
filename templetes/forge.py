#!/usr/bin/env pythfn3
"""CLI principal - Forge CLI Templates."""

import sys
import argparse
from pathlib import Path

# Adiciona o diretório atual ao path para importar core
sys.path.insert(0, str(Path(__file__).parent))

from core import generate, list_templates


def main():
    parser = argparse.ArgumentParser(
        description="Forge CLI - Gerador de templates",
        prog="forge",
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # Comando: list
    list_parser = subparsers.add_parser("list", help="Lista templates disponíveis")

    # Comando: new
    new_parser = subparsers.add_parser("new", help="Cria novo projeto a partir de template")
    new_parser.add_argument("template", help="Nome do template")
    new_parser.add_argument("path", nargs="?", help="Caminho de destino (opcional)")
    new_parser.add_argument("-n", "--name", help="Nome do projeto (sobrescreve o nome do diretório)")
    new_parser.add_argument("-a", "--author", help="Nome do autor")
    new_parser.add_argument("-d", "--description", help="Descrição do projeto")
    new_parser.add_argument("-v", "--version", default="0.1.0", help="Versão inicial do projeto (padrão: 0.1.0)")
    new_parser.add_argument("-o", "--output", dest="path", help="Caminho de destino (alternativa ao argumento posicional)")
    new_parser.add_argument("--no-venv", action="store_true", help="Não criar ambiente virtual automaticamente")
    new_parser.add_argument("--no-install", action="store_true", help="Não instalar dependências automaticamente")
    new_parser.add_argument("--template-dir", help="Diretório customizado de templates")

    args = parser.parse_args()

    if args.command == "list":
        templates = list_templates()
        if templates:
            print("Templates disponíveis:")
            for t in templates:
                print(f"  - {t}")
        else:
            print("Nenhum template disponível")

    elif args.command == "new":
        context = {}
        if args.name:
            context["project_name"] = args.name
        if args.author:
            context["author"] = args.author
        if args.description:
            context["description"] = args.description
        if args.version:
            context["version"] = args.version

        # Flags de controle
        skip_venv = getattr(args, "no_venv", False)
        skip_install = getattr(args, "no_install", False)
        template_dir = getattr(args, "template_dir", None)

        try:
            result = generate(
                args.template,
                args.path,
                context,
                skip_venv=skip_venv,
                skip_install=skip_install,
                template_dir=template_dir
            )
            print(f"✓ Projeto criado em: {result}")
        except ValueError as e:
            print(f"✗ Erro: {e}")
            sys.exit(1)
        except FileExistsError as e:
            print(f"✗ Erro: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
