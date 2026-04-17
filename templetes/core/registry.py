#!/usr/bin/env python3
# Registro inteligente de templates - JSON + detecção automática

import json
import os
from pathlib import Path
from typing import Optional


def get_templates_dir() -> Path:
    return Path(__file__).parent.parent / "templates"


def get_registry_path() -> Path:
    return get_templates_dir() / "templates.json"


def load_registry() -> dict:
    """Carrega o registro JSON de templates."""
    registry_path = get_registry_path()
    if registry_path.exists():
        return json.loads(registry_path.read_text(encoding="utf-8"))
    return {"version": "1.0.0", "templates": {}}


def save_registry(registry: dict) -> None:
    """Salva o registro JSON de templates."""
    registry_path = get_registry_path()
    registry_path.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def scan_templates() -> dict:
    """Escaneia diretório de templates e detecta automaticamente."""
    templates_dir = get_templates_dir()
    found = {}

    for item in templates_dir.iterdir():
        if not item.is_dir() or item.name.startswith("_"):
            continue

        template_id = item.name
        manifest_path = item / ".forge-template.json"

        # Se tem manifesto, carrega metadados
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                found[template_id] = _build_template_config(template_id, item, manifest)
                continue
            except (json.JSONDecodeError, IOError):
                pass

        # Detecção automática por estrutura
        found[template_id] = _detect_template_config(template_id, item)

    return found


def _build_template_config(tid: str, path: Path, manifest: dict) -> dict:
    """Constroi config a partir de manifesto."""
    return {
        "name": tid,
        "title": manifest.get("title", tid.replace("-", " ").title()),
        "description": manifest.get("description", ""),
        "category": manifest.get("category", "other"),
        "tags": manifest.get("tags", []),
        "variables": manifest.get("variables", {}),
        "post_create": manifest.get("post_create", {}),
        "source": "manifest",
        "path": str(path.relative_to(get_templates_dir()))
    }


def _detect_template_config(tid: str, path: Path) -> dict:
    """Detecta config automaticamente por análise de estrutura."""
    title = tid.replace("-", " ").replace("_", " ").title()
    category = "other"
    tags = []

    # Heurísticas por conteúdo
    files = {f.name for f in path.rglob("*") if f.is_file()}

    if any("fastapi" in f.lower() for f in files) or "requirements.txt" in files:
        if any(f.endswith(".py") and "route" in f for f in map(str, path.rglob("*.py"))):
            category = "api"
            tags = ["api", "fastapi", "rest"]
            title = f"API {title}"

    if (path / "commands").exists() or any("argparse" in f.read_text(encoding="utf-8", errors="ignore") for f in path.glob("*.py") if f.is_file()):
        category = "cli"
        tags = ["cli", "tool"]
        title = f"CLI {title}"

    # Detecta variáveis padrão
    variables = {"project_name": {"required": True, "default": tid}}

    # Escaneia arquivos por placeholders {{var}}
    for file in path.rglob("*"):
        if file.is_file() and file.suffix in {".py", ".txt", ".md", ".json", ".toml", ".yaml", ".yml", ""}:
            try:
                content = file.read_text(encoding="utf-8", errors="ignore")
                for line in content.split("\n"):
                    if "{{" in line and "}}" in line:
                        import re
                        for match in re.findall(r"\{\{(\w+)\}\}", content):
                            if match not in variables:
                                variables[match] = {"required": False, "default": "", "description": f"Variável {match}"}
            except (IOError, UnicodeDecodeError):
                continue

    return {
        "name": tid,
        "title": title,
        "description": f"Template {tid} (auto-detectado)",
        "category": category,
        "tags": tags,
        "variables": variables,
        "post_create": {},
        "source": "auto-detected",
        "path": str(path.relative_to(get_templates_dir()))
    }


def get_template_config(name: str) -> Optional[dict]:
    """Obtém config de um template por nome."""
    registry = load_registry()
    templates = registry.get("templates", {})

    # Busca direta
    if name in templates:
        return _enrich_config(templates[name])

    # Busca por título (case insensitive)
    name_lower = name.lower()
    for tid, config in templates.items():
        if config.get("title", "").lower() == name_lower:
            return _enrich_config(config)

    # Fallback: scan dinâmico se não está no registro
    scanned = scan_templates()
    if name in scanned:
        return _enrich_config(scanned[name])

    return None


def _enrich_config(config: dict) -> dict:
    """Enriquece config com caminho absoluto."""
    config = dict(config)
    config["full_path"] = str(get_templates_dir() / config.get("path", config["name"]))
    return config


def list_templates(flat: bool = False) -> list:
    """Lista templates disponíveis."""
    registry = load_registry()
    registered = registry.get("templates", {})

    # Merge com scan
    scanned = scan_templates()
    all_templates = {**scanned, **registered}  # Registro sobrescreve scan

    if flat:
        return sorted(all_templates.keys())

    # Agrupado por categoria
    by_category = {}
    for tid, config in sorted(all_templates.items()):
        cat = config.get("category", "other")
        by_category.setdefault(cat, []).append(config)

    return by_category


def sync_registry() -> dict:
    """Sincroniza registro: adiciona templates detectados, mantém metadados manuais."""
    registry = load_registry()
    scanned = scan_templates()

    changes = {"added": [], "updated": []}

    for tid, config in scanned.items():
        if tid not in registry.get("templates", {}):
            registry.setdefault("templates", {})[tid] = config
            changes["added"].append(tid)
        elif registry["templates"][tid].get("source") == "auto-detected":
            # Atualiza apenas se ainda é auto-detectado
            registry["templates"][tid] = config
            changes["updated"].append(tid)

    save_registry(registry)
    return changes


def add_template(name: str, title: str = None, description: str = "",
                 category: str = "other", tags: list = None,
                 variables: dict = None) -> bool:
    """Adiciona template manualmente ao registro."""
    registry = load_registry()

    if name in registry.get("templates", {}):
        return False

    registry.setdefault("templates", {})[name] = {
        "name": name,
        "title": title or name.replace("-", " ").title(),
        "description": description,
        "category": category,
        "tags": tags or [],
        "variables": variables or {"project_name": {"required": True, "default": name}},
        "source": "manual",
        "path": name
    }

    save_registry(registry)
    return True


def get_template_variables(name: str) -> dict:
    """Retorna variáveis de um template com defaults resolvidos."""
    config = get_template_config(name)
    if not config:
        return {}

    variables = config.get("variables", {})
    resolved = {}

    for key, var_config in variables.items():
        default = var_config.get("default", "")
        if isinstance(default, str) and default.startswith("$"):
            default = os.getenv(default[1:], "")
        resolved[key] = {**var_config, "resolved_default": default}

    return resolved
