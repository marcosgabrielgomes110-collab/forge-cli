#!/usr/bin/env python3
# Gerador de templates - usa registry JSON com fallback para scan

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from .registry import get_template_config, list_templates


def get_workspace_dir() -> Path:
    return Path.cwd()


def render_template(content: str, context: dict) -> str:
    """Substitui variáveis {{key}} no conteúdo."""
    result = content
    for key, value in context.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


def is_text_file(file_path: Path) -> bool:
    exts = {".py", ".txt", ".md", ".json", ".yaml", ".yml", ".toml",
            ".cfg", ".ini", ".html", ".css", ".js", ".sh", ".bash", ".zsh", ".dockerfile", ""}
    return file_path.suffix.lower() in exts


def generate(template_name: str, target_path: str = None, context: dict = None,
             skip_venv: bool = False, skip_install: bool = False, template_dir: str = None) -> Path:
    """Gera projeto a partir de template registrado."""

    # Carrega config do template
    config = get_template_config(template_name)

    if not config:
        available = list_templates(flat=True)
        raise ValueError(
            f"Template '{template_name}' não encontrado. "
            f"Disponíveis: {', '.join(available) or 'nenhum'}"
        )

    template_path = Path(config.get("full_path"))
    if template_dir:
        template_path = Path(template_dir).expanduser().resolve() / template_name

    if not template_path.exists():
        raise ValueError(f"Diretório do template não existe: {template_path}")

    # Resolve caminho de destino
    if target_path is None:
        target = get_workspace_dir() / template_name.replace("-", "_")
    else:
        target = Path(target_path).resolve()

    if target.exists():
        raise FileExistsError(f"Diretório já existe: {target}")

    # Contexto com defaults do template
    variables = config.get("variables", {})
    default_ctx = {
        "project_name": target.name,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "author": os.getenv("USER", "unknown"),
        "description": "",
        "version": "0.1.0",
    }

    # Aplica defaults do registro
    for key, var_cfg in variables.items():
        default = var_cfg.get("default", "")
        if isinstance(default, str) and default.startswith("$"):
            default = os.getenv(default[1:], "")
        default_ctx.setdefault(key, default)

    if context:
        default_ctx.update(context)

    # Copia estrutura
    shutil.copytree(template_path, target)

    # Renderiza templates
    for file_path in target.rglob("*"):
        if file_path.is_file() and is_text_file(file_path):
            try:
                content = file_path.read_text(encoding="utf-8")
                rendered = render_template(content, default_ctx)
                if content != rendered:
                    file_path.write_text(rendered, encoding="utf-8")
            except (UnicodeDecodeError, PermissionError, IOError):
                pass

    # Venv e dependências
    venv_path = _create_venv(target) if not skip_venv else None
    if venv_path and not skip_install:
        _install_deps(target, venv_path)

    # Instruções pós-criação
    _print_instructions(config, target)

    return target


def _create_venv(target: Path) -> Optional[Path]:
    venv_path = target / ".venv"
    print(f"→ Criando ambiente virtual...")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True, capture_output=True
        )
        print(f"✓ Ambiente virtual criado")
        return venv_path
    except subprocess.CalledProcessError as e:
        print(f"⚠ Falha ao criar .venv: {e}")
        return None


def _install_deps(target: Path, venv_path: Path) -> None:
    pip = venv_path / "bin" / "pip"
    if not pip.exists():
        pip = venv_path / "Scripts" / "pip.exe"  # Windows

    req_file = target / "requirements.txt"
    pyproject = target / "pyproject.toml"

    if req_file.exists():
        print(f"→ Instalando dependências...")
        try:
            subprocess.run([str(pip), "install", "-r", str(req_file)],
                         check=True, capture_output=True)
            print(f"✓ Dependências instaladas")
        except subprocess.CalledProcessError as e:
            print(f"⚠ Falha: {e}")
    elif pyproject.exists():
        print(f"→ Instalando em modo desenvolvimento...")
        try:
            subprocess.run([str(pip), "install", "-e", str(target)],
                         check=True, capture_output=True)
            print(f"✓ Pacote instalado")
        except subprocess.CalledProcessError as e:
            print(f"⚠ Falha: {e}")


def _print_instructions(config: dict, target: Path) -> None:
    post = config.get("post_create", {})
    entry = post.get("entry_point", "main.py")
    port = post.get("port")

    print("\n" + "=" * 50)
    print(f"✓ Projeto '{target.name}' criado em: {target}")
    print("=" * 50)
    print(f"\n📋 Próximos passos:\n")
    print(f"  cd {target}")

    if (target / ".venv").exists():
        print(f"  source .venv/bin/activate")

    for instr in post.get("instructions", [f"Veja README.md para instruções"]):
        print(f"  {instr}")

    if port:
        print(f"\n  Acesse: http://localhost:{port}")
    print()


