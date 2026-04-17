#!/usr/bin/env python3
# CLI principal - Forge CLI Templates

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core import generate, list_templates, sync_registry, add_template


def cmd_list():
    """Lista templates agrupados por categoria."""
    templates = list_templates(flat=False)

    if not templates:
        print("Nenhum template encontrado.")
        print(f"Diretório: {Path(__file__).parent / 'templates'}")
        return

    print("\n📦 Templates Disponíveis:\n")

    for category, configs in sorted(templates.items()):
        emoji = {"api": "🔌", "cli": "⌨️ ", "web": "🌐", "other": "📁"}.get(category, "📁")
        print(f"  {emoji} {category.upper()}")

        for cfg in configs:
            title = cfg.get("title", cfg["name"])
            desc = cfg.get("description", "")
            source = cfg.get("source", "")
            src_marker = "📝" if source == "manual" else "🔍" if source == "auto-detected" else ""

            print(f"     • {title} ({cfg['name']}) {src_marker}")
            if desc:
                print(f"       └─ {desc[:50]}{'...' if len(desc) > 50 else ''}")
        print()


def cmd_sync():
    """Sincroniza templates detectados com o registro."""
    changes = sync_registry()

    if changes["added"]:
        print(f"✓ Adicionados: {', '.join(changes['added'])}")
    if changes["updated"]:
        print(f"↻ Atualizados: {', '.join(changes['updated'])}")

    if not changes["added"] and not changes["updated"]:
        print("✓ Registro já está sincronizado")


def cmd_new(args):
    """Cria novo projeto a partir de template."""
    context = {}
    if getattr(args, "name", None):
        context["project_name"] = args.name
    if getattr(args, "author", None):
        context["author"] = args.author
    if getattr(args, "description", None):
        context["description"] = args.description
    if getattr(args, "version", None):
        context["version"] = args.version

    target = args.path if hasattr(args, "path") else None
    if hasattr(args, "output") and args.output:
        target = args.output

    try:
        result = generate(
            args.template,
            target,
            context,
            skip_venv=getattr(args, "no_venv", False),
            skip_install=getattr(args, "no_install", False),
            template_dir=getattr(args, "template_dir", None)
        )
        print(f"✓ Projeto criado em: {result}")
    except ValueError as e:
        print(f"✗ Erro: {e}")
        sys.exit(1)
    except FileExistsError as e:
        print(f"✗ Erro: {e}")
        sys.exit(1)


def cmd_info(template_name):
    """Mostra informações detalhadas de um template."""
    from core.registry import get_template_config, get_template_variables

    config = get_template_config(template_name)
    if not config:
        print(f"✗ Template '{template_name}' não encontrado")
        return

    print(f"\n📋 Template: {config.get('title', template_name)}\n")
    print(f"  ID: {config['name']}")
    print(f"  Descrição: {config.get('description', 'N/A')}")
    print(f"  Categoria: {config.get('category', 'other')}")
    print(f"  Tags: {', '.join(config.get('tags', [])) or 'N/A'}")
    print(f"  Origem: {config.get('source', 'N/A')}")

    variables = get_template_variables(template_name)
    if variables:
        print(f"\n  Variáveis disponíveis:")
        for key, cfg in variables.items():
            req = "obrigatória" if cfg.get("required") else "opcional"
            default = cfg.get("resolved_default", cfg.get("default", ""))
            print(f"    • {key} ({req}, default: '{default}')")
    print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Forge CLI - Gerador de templates inteligente",
        prog="forge",
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos")

    # list
    subparsers.add_parser("list", help="Lista templates disponíveis")

    # new
    new_p = subparsers.add_parser("new", help="Cria novo projeto")
    new_p.add_argument("template", help="Nome do template")
    new_p.add_argument("path", nargs="?", help="Caminho de destino")
    new_p.add_argument("-n", "--name", help="Nome do projeto")
    new_p.add_argument("-a", "--author", help="Nome do autor")
    new_p.add_argument("-d", "--description", help="Descrição")
    new_p.add_argument("-v", "--version", default="0.1.0", help="Versão")
    new_p.add_argument("-o", "--output", dest="path", help="Caminho de destino")
    new_p.add_argument("--no-venv", action="store_true", help="Sem venv")
    new_p.add_argument("--no-install", action="store_true", help="Sem deps")
    new_p.add_argument("--template-dir", help="Diretório customizado")

    # sync
    subparsers.add_parser("sync", help="Sincroniza templates com registro")

    # info
    info_p = subparsers.add_parser("info", help="Informações do template")
    info_p.add_argument("template", help="Nome do template")

    args = parser.parse_args()

    cmds = {
        "list": cmd_list,
        "sync": cmd_sync,
        "new": lambda: cmd_new(args),
        "info": lambda: cmd_info(args.template),
    }

    if args.command in cmds:
        cmds[args.command]()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
