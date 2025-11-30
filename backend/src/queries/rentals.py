from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.queries import Repository
from src.models.rental import Rental

from pydantic import BaseModel

class RentalResponse(BaseModel):
    id: UUID
    item_id: UUID
    tenant_id: UUID
    status: str
    total_price: float
    starts_at: str
    ends_at: str

    class Config:
        from_attributes = True

async def get_user_rentals(db: AsyncSession, user_id: UUID) -> List[RentalResponse]:
    repo = Repository(db)
    rentals = await repo.rentals.get_active_rentals_for_user(user_id)
    return [RentalResponse.model_validate(r) for r in rentals]