from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..dependencies import get_db
from src.models.item import Item
from src.queries.orm import Repository

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/")
async def search_items(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius: float = Query(5.0, ge=0.1, le=100),
    db: AsyncSession = Depends(get_db)
):
    repo = Repository(db)
    items = await repo.items.get_available_items_near(lat, lon, radius)
    return items

@router.get("/{item_id}")
async def get_item(item_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = Repository(db)
    item = await repo.items.get_by_id(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item