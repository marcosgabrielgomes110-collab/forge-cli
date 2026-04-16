#!/usr/bin/env python3
"""Entry point para execução direta do Forge CLI."""

import sys
from pathlib import Path

# Adiciona o diretório templetes ao path
sys.path.insert(0, str(Path(__file__).parent / "templetes"))

from forge import main

if __name__ == "__main__":
    main()
