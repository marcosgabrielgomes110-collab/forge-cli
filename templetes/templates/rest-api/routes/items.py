"""Rotas de exemplo - Items API.

Demonstra endpoints com filtros e paginação.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional

from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/items",
    tags=["items"],
)


class Item(BaseModel):
    id: int
    name: str
    price: float
    category: str


# Fake database
ITEMS_DB = [
    {"id": 1, "name": "Notebook", "price": 5000.0, "category": "eletrônicos"},
    {"id": 2, "name": "Mouse", "price": 100.0, "category": "eletrônicos"},
    {"id": 3, "name": "Teclado", "price": 300.0, "category": "eletrônicos"},
    {"id": 4, "name": "Caderno", "price": 25.0, "category": "papelaria"},
]


@router.get("/", response_model=List[Item])
async def list_items(
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    min_price: Optional[float] = Query(None, ge=0, description="Preço mínimo"),
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de registros"),
):
    """Lista items com filtros e paginação."""
    logger.debug(f"Listando items: category={category}, skip={skip}, limit={limit}")

    result = ITEMS_DB

    if category:
        result = [i for i in result if i["category"] == category]

    if min_price is not None:
        result = [i for i in result if i["price"] >= min_price]

    return result[skip:skip + limit]


@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """Obtém um item pelo ID."""
    for item in ITEMS_DB:
        if item["id"] == item_id:
            return item
    from fastapi import HTTPException, status
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
