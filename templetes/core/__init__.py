# Core module - gerador de templates
from .generate import generate
from .registry import list_templates, get_template_config, sync_registry, add_template

__all__ = ["generate", "list_templates", "get_template_config", "sync_registry", "add_template"]
