#!/usr/bin/env python3
"""Gerador de templates - copia estrutura de templates para o workspace."""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def get_templates_dir() -> Path:
    """Retorna o diretório onde os templates estão armazenados."""
    # Templates ficam ao lado do core/ na pasta templates/
    return Path(__file__).parent.parent / "templates"


def get_workspace_dir() -> Path:
    """Retorna o diretório onde o comando está sendo executado (cwd)."""
    return Path.cwd()


def render_template(content: str, context: dict) -> str:
    """Substitui variáveis no conteúdo do template.

    Exemplo de variáveis:
        {{project_name}} -> nome do projeto
        {{author}} -> nome do autor
        {{created_at}} -> data de criação
    """
    result = content
    for key, value in context.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


def generate(template_name: str, target_path: str = None, context: dict = None,
             skip_venv: bool = False, skip_install: bool = False, template_dir: str = None) -> Path:
    """Gera um projeto a partir de um template.

    Args:
        template_name: Nome da pasta do template (ex: 'rest-api', 'cli-tool')
        target_path: Caminho onde gerar (padrão: cwd + nome do template)
        context: Dicionário de variáveis para substituir nos arquivos
        skip_venv: Se True, não cria ambiente virtual
        skip_install: Se True, não instala dependências
        template_dir: Diretório customizado de templates (opcional)

    Returns:
        Path para o diretório criado

    Raises:
        ValueError: Se o template não existir
        FileExistsError: Se o diretório alvo já existir
    """
    if template_dir:
        templates_dir = Path(template_dir).expanduser().resolve()
    else:
        templates_dir = get_templates_dir()
    template_path = templates_dir / template_name

    if not template_path.exists():
        available = [d.name for d in templates_dir.iterdir() if d.is_dir()]
        raise ValueError(
            f"Template '{template_name}' não encontrado. "
            f"Disponíveis: {', '.join(available) or 'nenhum'}"
        )

    # Define diretório de destino
    if target_path is None:
        target_path = get_workspace_dir() / template_name.replace("-", "_")
    else:
        target_path = Path(target_path).resolve()

    if target_path.exists():
        raise FileExistsError(f"Diretório já existe: {target_path}")

    # Contexto padrão
    default_context = {
        "project_name": target_path.name,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "author": os.getenv("USER", "unknown"),
        "description": "",
        "version": "0.1.0",
    }
    if context:
        default_context.update(context)

    # Copia estrutura
    shutil.copytree(template_path, target_path)

    # Processa arquivos para substituir variáveis
    for file_path in target_path.rglob("*"):
        if file_path.is_file() and is_text_file(file_path):
            try:
                content = file_path.read_text(encoding="utf-8")
                rendered = render_template(content, default_context)
                if content != rendered:
                    file_path.write_text(rendered, encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                pass  # Ignora arquivos binários ou sem permissão

    # Cria ambiente virtual
    venv_path = None
    if not skip_venv:
        venv_path = target_path / ".venv"
        print(f"→ Criando ambiente virtual em {venv_path}...")
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True,
                capture_output=True,
            )
            print(f"✓ Ambiente virtual criado")
        except subprocess.CalledProcessError as e:
            print(f"⚠ Falha ao criar .venv: {e}")
            venv_path = None

    # Instala dependências
    if venv_path and not skip_install:
        pip_path = venv_path / "bin" / "pip"
        if not pip_path.exists():
            pip_path = venv_path / "Scripts" / "pip.exe"  # Windows

        # Verifica se há requirements.txt ou pyproject.toml
        req_file = target_path / "requirements.txt"
        pyproject_file = target_path / "pyproject.toml"

        if req_file.exists():
            print(f"→ Instalando dependências de requirements.txt...")
            try:
                subprocess.run(
                    [str(pip_path), "install", "-r", str(req_file)],
                    check=True,
                    capture_output=True,
                )
                print(f"✓ Dependências instaladas")
            except subprocess.CalledProcessError as e:
                print(f"⚠ Falha ao instalar dependências: {e}")
        elif pyproject_file.exists():
            print(f"→ Instalando pacote em modo desenvolvimento...")
            try:
                subprocess.run(
                    [str(pip_path), "install", "-e", str(target_path)],
                    check=True,
                    capture_output=True,
                )
                print(f"✓ Pacote instalado")
            except subprocess.CalledProcessError as e:
                print(f"⚠ Falha ao instalar pacote: {e}")

    # Imprime instruções
    print("\n" + "=" * 50)
    print(f"✓ Projeto '{target_path.name}' criado em: {target_path}")
    print("=" * 50)
    print("\n📋 PRÓXIMOS PASSOS:\n")
    print(f"  1. Entre na pasta:")
    print(f"     cd {target_path}")
    print()
    print(f"  2. Ative o ambiente virtual:")
    if os.name == "nt":  # Windows
        print(f"     .venv\\Scripts\\activate")
    else:  # Unix
        print(f"     source .venv/bin/activate")
    print()

    # Instruções específicas por template
    if template_name == "cli-tool":
        print(f"  3. Execute a CLI:")
        print(f"     python main.py --help")
        print(f"     python main.py hello")
        print()
        print(f"  4. Ou instale globalmente:")
        print(f"     pip install -e .")
        print(f"     {target_path.name} --help")
    elif template_name == "rest-api":
        print(f"  3. Execute a API:")
        print(f"     python main.py")
        print()
        print(f"  4. Acesse a documentação:")
        print(f"     http://localhost:8000/docs")
    else:
        print(f"  3. Veja o README para instruções:")
        print(f"     cat README.md")

    print()
    return target_path


def is_text_file(file_path: Path) -> bool:
    """Heurística simples para detectar se arquivo é texto."""
    text_extensions = {
        ".py", ".txt", ".md", ".json", ".yaml", ".yml",
        ".toml", ".cfg", ".ini", ".html", ".css", ".js",
        ".sh", ".bash", ".zsh", ".dockerfile", ".gitignore",
        "",  # arquivos sem extensão
    }
    return file_path.suffix.lower() in text_extensions


def list_templates() -> list:
    """Lista templates disponíveis."""
    templates_dir = get_templates_dir()
    if not templates_dir.exists():
        return []
    return [
        d.name for d in templates_dir.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    ]


if __name__ == "__main__":
    # Exemplo de uso standalone
    import sys

    if len(sys.argv) < 2:
        print("Uso: python generate.py <nome_template> [caminho_destino]")
        print(f"\nTemplates disponíveis: {', '.join(list_templates()) or 'nenhum'}")
        sys.exit(1)

    template = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = generate(template, target)
        print(f"✓ Template '{template}' gerado em: {result}")
    except Exception as e:
        print(f"✗ Erro: {e}")
        sys.exit(1)
