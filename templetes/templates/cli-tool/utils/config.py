"""Configurações da aplicação."""

import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).parent.parent

# Configurações padrão
DEFAULT_CONFIG = {
    "log_level": "INFO",
    "log_file": None,  # ou "logs/app.log" para salvar em arquivo
}


def get_config():
    """Retorna configuração mesclada (padrão + env vars).

    Variáveis de ambiente suportadas:
        {{project_name|upper}}_LOG_LEVEL   - Nível de logging
        {{project_name|upper}}_LOG_FILE    - Arquivo de log (opcional)
    """
    config = DEFAULT_CONFIG.copy()
    prefix = "{{project_name|upper}}_"

    # Carrega de variáveis de ambiente
    if os.getenv(f"{prefix}LOG_LEVEL"):
        config["log_level"] = os.getenv(f"{prefix}LOG_LEVEL")

    if os.getenv(f"{prefix}LOG_FILE"):
        config["log_file"] = os.getenv(f"{prefix}LOG_FILE")

    # Carrega de arquivo .env se existir
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.strip() and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                if key == "LOG_LEVEL":
                    config["log_level"] = value.strip().strip('"\'')
                elif key == "LOG_FILE":
                    config["log_file"] = value.strip().strip('"\'')

    return config
