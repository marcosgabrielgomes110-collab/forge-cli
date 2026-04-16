# {{project_name}}

{{description}}

Gerada em {{created_at}} por {{author}}.

## Instalação

```bash
uv pip install -r requirements.txt
# ou: pip install -r requirements.txt
```

## Executar

```bash
python main.py
# ou: uvicorn main:app --reload
```

## Endpoints

- `GET /` - Mensagem de boas-vindas
- `GET /health` - Health check
- `GET /users` - Lista usuários
- `GET /items` - Lista items

## Como adicionar uma nova rota

**Passo 1:** Crie um arquivo em `routes/` com o nome do seu recurso (ex: `products.py`)

**Passo 2:** Copie este template e ajuste:

```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/products",      # URL base
    tags=["products"],       # Nome da tag na documentação
)

@router.get("/")
async def list_products():
    return {"products": []}

@router.get("/{id}")
async def get_product(id: int):
    return {"id": id, "name": "Produto"}
```

**Pronto!** A rota aparece automaticamente em `/products`.

## Configuração (.env)

Crie um arquivo `.env` na raiz:

```
LOG_LEVEL=DEBUG
PORT=8080
```

Variáveis disponíveis: `LOG_LEVEL`, `LOG_FILE`, `HOST`, `PORT`, `RELOAD`, `ENABLE_DOCS`, `CORS_ORIGINS`
