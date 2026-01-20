from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import datetime, time

from src.queries import Repository
from src.models.rental import Rental
from src.models.item import Item

from pydantic import BaseModel

class RentalCreate(BaseModel):
    item_id: UUID
    tenant_id: UUID
    starts_at: datetime 
    ends_at: datetime    

class RentalResponse(BaseModel):
    id: UUID
    item_id: UUID
    tenant_id: UUID
    status: str
    total_price: float
    starts_at: datetime
    ends_at: datetime

    class Config:
        from_attributes = True

async def create_rental(db: AsyncSession, rental: RentalCreate) -> RentalResponse:
    repo = Repository(db)
    
    # Проверка на существование предмета
    item = await repo.items.get_by_id(Item, rental.item_id)
    if not item:
        raise ValueError("Item not found")
    
    # Проверка статуса доступности
    if not item.is_available:
        raise ValueError("Item is not available for rent")
    
        
    if rental.ends_at <= rental.starts_at:
        raise ValueError("End date must be after start date")
        
    
    # Условный пример автоматического расчёта цены
    duration_hours = (rental.ends_at - rental.starts_at).total_seconds() / 3600
    if duration_hours <= 24:
        total_price = float(item.price_per_hour or 0) * duration_hours
    else:
        days = (rental.ends_at - rental.starts_at).days
        total_price = float(item.price_per_day or 0) * days
    
    rental_data = {
        "item_id": rental.item_id,
        "tenant_id": rental.tenant_id,
        "status": "pending",
        "total_price": round(total_price, 2),
        "starts_at": rental.starts_at,
        "ends_at": rental.ends_at
    }
    
    db_rental = await repo.rentals.create(Rental, **rental_data)
    return RentalResponse.model_validate(db_rental)

async def get_user_rentals(db: AsyncSession, user_id: UUID) -> List[RentalResponse]:
    repo = Repository(db)
    rentals = await repo.rentals.get_active_rentals_for_user(user_id)
    return [RentalResponse.model_validate(r) for r in rentals]

async def confirm_rental(db: AsyncSession, rental_id: UUID, current_user: UUID) -> RentalResponse:
    """Подтверждение аренды владельцем предмета"""
    repo = Repository(db)
    rental = await repo.rentals.get_by_id(Rental, rental_id)
    if not rental:
        raise ValueError("Rental not found")
    
    # Проверка владельца
    item = await repo.items.get_by_id(Item, rental.item_id)
    if item.owner_id != current_user:
        raise ValueError("Only owner can confirm rental")
    
    rental.status = "confirmed"
    await repo.session.commit()
    await repo.session.refresh(rental)
    return RentalResponse.model_validate(rental)