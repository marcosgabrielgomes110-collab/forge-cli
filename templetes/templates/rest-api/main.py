#!/usr/bin/env python3
"""{{project_name}} - API REST Modular

Estrutura:
  routes/       - Coloque suas rotas aqui (cada arquivo = um router)
  utils/        - Utilitários (logging, config, etc)
  middleware/   - Middlewares customizados
  main.py       - Entry point (não precisa editar)

Para adicionar rotas:
  1. Crie um arquivo em routes/<nome>.py
  2. Crie um APIRouter e exporte como 'router'
  3. Pronto! As rotas serão registradas automaticamente.

Exemplo em routes/users.py:
  from fastapi import APIRouter
  router = APIRouter(prefix="/users", tags=["users"])

  @router.get("/")
  async def list_users():
      return {"users": []}
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.logger import get_logger, setup_logging
from utils.config import get_config
from routes import discover_routers

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Factory function para criar a aplicação FastAPI."""
    config = get_config()
    setup_logging(config.get("log_level", "INFO"))

    app = FastAPI(
        title="{{project_name}}",
        description="API REST modular gerada em {{created_at}} por {{author}}",
        version="0.1.0",
        docs_url="/docs" if config.get("enable_docs", True) else None,
        redoc_url="/redoc" if config.get("enable_docs", True) else None,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get("cors_origins", ["*"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware de logging
    from middleware.logging import LoggingMiddleware
    app.add_middleware(LoggingMiddleware)

    # Registra rotas automaticamente
    routers = discover_routers()
    for router in routers:
        app.include_router(router)
        logger.debug(f"Router registrado: {router.prefix or '/'} ({router.tags})")

    # Health check padrão
    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok", "version": "0.1.0"}

    # Root
    @app.get("/", tags=["root"])
    async def root():
        return {
            "message": "Bem-vindo à {{project_name}}",
            "docs": "/docs",
            "health": "/health",
        }

    logger.info(f"Aplicação {{project_name}} iniciada")
    return app


app = create_app()


if __name__ == "__main__":
    config = get_config()
    uvicorn.run(
        "main:app",
        host=config.get("host", "0.0.0.0"),
        port=config.get("port", 8000),
        reload=config.get("reload", True),
        log_level=config.get("log_level", "INFO").lower(),
    )
