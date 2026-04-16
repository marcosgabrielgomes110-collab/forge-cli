"""Configurações centralizadas da API."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

DEFAULT_CONFIG = {
    "log_level": "INFO",
    "log_file": None,
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,
    "enable_docs": True,
    "cors_origins": ["*"],
}


def get_config():
    """Retorna configuração mesclada (padrão + env vars + .env)."""
    config = DEFAULT_CONFIG.copy()
    prefix = "{{project_name|upper}}_"

    # Variáveis de ambiente
    env_vars = [
        ("LOG_LEVEL", "log_level"),
        ("LOG_FILE", "log_file"),
        ("HOST", "host"),
        ("PORT", "port", int),
        ("RELOAD", "reload", lambda x: x.lower() == "true"),
        ("ENABLE_DOCS", "enable_docs", lambda x: x.lower() == "true"),
    ]

    for var_name, config_key, *transform in env_vars:
        env_val = os.getenv(f"{prefix}{var_name}")
        if env_val:
            if transform:
                try:
                    config[config_key] = transform[0](env_val)
                except (ValueError, AttributeError):
                    pass
            else:
                config[config_key] = env_val

    # Arquivo .env
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key, val = key.strip(), val.strip().strip('"\'')

            if key == "CORS_ORIGINS":
                config["cors_origins"] = [v.strip() for v in val.split(",")]
            elif key in [v[1].upper() for v in env_vars]:
                config_key = next(c for _, c, *_ in env_vars if c.upper() == key)
                transform = next((t for _, c, *t in env_vars if c.upper() == key), None)
                if transform:
                    try:
                        config[config_key] = transform[0](val)
                    except:
                        config[config_key] = val
                else:
                    config[config_key] = val

    return config
