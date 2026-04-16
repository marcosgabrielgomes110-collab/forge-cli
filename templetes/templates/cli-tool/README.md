# {{project_name}}

{{description}}

Gerada em {{created_at}} por {{author}}.

## Instalação

```bash
uv pip install -e .
# ou: pip install -e .
```

## Uso

```bash
# Ver todos os comandos
python main.py --help

# Rodar comando hello
python main.py hello

# Rodar comando status
python main.py status --full
```

## Como adicionar um comando novo

**Passo 1:** Crie um arquivo em `commands/` (ex: `meucmd.py`)

**Passo 2:** Copie este template e ajuste:

```python
def add_subparser(subparsers):
    # Define nome e descrição
    parser = subparsers.add_parser("meucmd", help="Meu comando")

    # Adicione argumentos
    parser.add_argument("--nome", help="Nome")
    parser.set_defaults(func=main)

def main(args):
    # args.nome contém o valor do --nome
    print(f"Olá {args.nome}!")
```

**Pronto!** Rode `python main.py meucmd --nome Fulano`

## Configuração (.env)

Crie um arquivo `.env` na raiz:

```
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log
```

Variáveis disponíveis: `LOG_LEVEL`, `LOG_FILE`
