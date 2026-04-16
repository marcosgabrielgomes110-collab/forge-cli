"""Rotas - descoberta automática de routers.

Este módulo descobre automaticamente todos os routers em routes/.
"""

import importlib
from pathlib import Path
from fastapi import APIRouter

from utils.logger import get_logger

logger = get_logger(__name__)


def discover_routers():
    """Descobre automaticamente todos os routers em routes/."""
    routes_dir = Path(__file__).parent
    routers = []

    for file in routes_dir.glob("*.py"):
        if file.name.startswith("_"):
            continue
        module_name = file.stem
        try:
            module = importlib.import_module(f"routes.{module_name}")
            if hasattr(module, "router") and isinstance(module.router, APIRouter):
                routers.append(module.router)
                logger.info(f"Router carregado: {module_name}")
            else:
                logger.warning(f"Módulo {module_name} não exporta um 'router'")
        except Exception as e:
            logger.error(f"Erro ao carregar router {module_name}: {e}")

    return routers
