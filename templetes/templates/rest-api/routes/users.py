"""Exemplo de rotas - Users API.

Para criar seu próprio módulo de rotas:
1. Copie este arquivo
2. Altere o nome (ex: products.py)
3. Ajuste prefix, tags e implemente seus endpoints
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List

from utils.logger import get_logger

logger = get_logger(__name__)

# Cria o router com prefixo e tags
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


# Schemas Pydantic
class User(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "João Silva",
                "email": "joao@exemplo.com",
            }
        }


class UserCreate(BaseModel):
    name: str
    email: str


# Fake database (substitua por um banco real)
USERS_DB = [
    {"id": 1, "name": "João Silva", "email": "joao@exemplo.com"},
    {"id": 2, "name": "Maria Souza", "email": "maria@exemplo.com"},
]


@router.get("/", response_model=List[User])
async def list_users():
    """Lista todos os usuários."""
    logger.info("Listando usuários")
    return USERS_DB


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Obtém um usuário pelo ID."""
    logger.info(f"Buscando usuário {user_id}")
    for user in USERS_DB:
        if user["id"] == user_id:
            return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuário não encontrado"
    )


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Cria um novo usuário."""
    logger.info(f"Criando usuário: {user.name}")
    new_id = max(u["id"] for u in USERS_DB) + 1
    new_user = {
        "id": new_id,
        "name": user.name,
        "email": user.email,
    }
    USERS_DB.append(new_user)
    logger.info(f"Usuário criado com ID {new_id}")
    return new_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Remove um usuário."""
    logger.info(f"Removendo usuário {user_id}")
    for i, user in enumerate(USERS_DB):
        if user["id"] == user_id:
            USERS_DB.pop(i)
            logger.info(f"Usuário {user_id} removido")
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuário não encontrado"
    )
