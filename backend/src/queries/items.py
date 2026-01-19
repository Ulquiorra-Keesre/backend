from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from src.queries import Repository
from src.models.item import Item

from pydantic import BaseModel
from typing import List as PydList

class ItemCreate(BaseModel):
    owner_id: UUID
    category_id: UUID
    title: str
    description: Optional[str] = None
    price_per_hour: Optional[float] = None
    price_per_day: Optional[float] = None
    address: str
    latitude: float
    longitude: float
    image_urls: PydList[str] = []
    is_available: bool = True

class ItemResponse(BaseModel):
    id: UUID
    owner_id: UUID
    category_id: UUID
    title: str
    description: Optional[str]
    price_per_hour: Optional[float]
    price_per_day: Optional[float]
    address: str
    latitude: float
    longitude: float
    is_available: bool

    class Config:
        from_attributes = True

    @staticmethod
    def from_orm(item: Item) -> "ItemResponse":
        return ItemResponse(
            id=item.id,
            owner_id=item.owner_id,
            category_id=item.category_id,
            title=item.title,
            description=item.description,
            price_per_hour=float(item.price_per_hour) if item.price_per_hour else None,
            price_per_day=float(item.price_per_day) if item.price_per_day else None,
            address=item.address,
            latitude=float(item.latitude),
            longitude=float(item.longitude),
            is_available=item.is_available,
            # image_urls=[img.image_url for img in sorted(item.images, key=lambda x: x.order_index)],
            # created_at=item.created_at.isoformat() if item.created_at else ""
        )


async def create_item(db: AsyncSession, item: ItemCreate) -> ItemResponse:
    repo = Repository(db)
    item_data = item.dict(exclude={"image_urls"})
    db_item = await repo.items.create_with_images(item_data, item.image_urls)
    return ItemResponse.from_orm(db_item)

async def search_items_near(
    db: AsyncSession, lat: float, lon: float, radius_km: float = 5.0
) -> List[ItemResponse]:
    repo = Repository(db)
    items = await repo.items.get_available_items_near(lat, lon, radius_km)
    return [ItemResponse.model_validate(item) for item in items]

async def get_item_by_id(db: AsyncSession, item_id: UUID) -> Optional[ItemResponse]:
    repo = Repository(db)
    item = await repo.items.get_by_id(Item, item_id)
    return ItemResponse.model_validate(item) if item else None