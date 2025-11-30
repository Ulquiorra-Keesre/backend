from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime

from src.api.dependencies import DatabaseDep, CurrentUser
from src.queries import Repository
from src.models.rental import Rental
from src.models.item import Item

router = APIRouter(prefix="/rentals", tags=["Rentals"])


# --- Схемы запросов ---
class RentalCreate(BaseModel):
    item_id: UUID
    starts_at: str  # ISO 8601, например: "2025-12-01T10:00:00Z"
    ends_at: str
    total_price: float = Field(gt=0)


# --- Роуты ---
@router.get("/me")
async def get_my_rentals(
    current_user: CurrentUser,
    db: DatabaseDep
):
    """Получить все активные аренды текущего пользователя (и как арендатор, и как владелец)"""
    repo = Repository(db)
    rentals = await repo.rentals.get_active_rentals_for_user(current_user)
    return rentals


@router.post("/", response_model=dict)
async def create_rental(rental: RentalCreate, current_user: CurrentUser, db: DatabaseDep):

    repo = Repository(db)

    item = await repo.items.get_by_id(rental.item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")

    if item.owner_id == current_user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot rent your own item")

    if not item.is_available:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Item is not available for rent")

    try:
        starts_at = datetime.fromisoformat(rental.starts_at.replace("Z", "+00:00"))
        ends_at = datetime.fromisoformat(rental.ends_at.replace("Z", "+00:00"))
        if ends_at <= starts_at:
            raise ValueError("End time must be after start time")
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid datetime format: {e}")
    
    rental = await repo.rentals.create(
        Rental,
        item_id=rental.item_id,
        tenant_id=current_user,
        status="pending",  # или "requested"
        total_price=rental.total_price,
        starts_at=starts_at,
        ends_at=ends_at,
        owner_confirmation=False,
        tenant_confirmation=False
    )

    return {
        "id": rental.id,
        "item_id": rental.item_id,
        "tenant_id": rental.tenant_id,
        "status": rental.status,
        "total_price": float(rental.total_price),
        "starts_at": rental.starts_at.isoformat(),
        "ends_at": rental.ends_at.isoformat()
    }

@router.post("/{rental_id}/confirm", response_model=dict)
async def confirm_rental(
    rental_id: UUID,
    current_user: CurrentUser,
    db: DatabaseDep
):
    
    repo = Repository(db)

    rental = await repo.rentals.get_by_id(rental_id)
    if not rental:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rental not found")

    item = await repo.items.get_by_id(rental.item_id)
    if current_user not in (rental.tenant_id, item.owner_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not involved in this rental")
    
    update_data = {}
    if current_user == rental.tenant_id:
        if rental.tenant_confirmation:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "You have already confirmed")
        update_data["tenant_confirmation"] = True
    elif current_user == item.owner_id:
        if rental.owner_confirmation:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Owner has already confirmed")
        update_data["owner_confirmation"] = True

    await repo.rentals.update(rental_id, **update_data)

    if rental.owner_confirmation and rental.tenant_confirmation:
        await repo.rentals.update(rental_id, status="active", confirmed_at=datetime.utcnow())

    updated_rental = await repo.rentals.get_by_id(rental_id)

    return {
        "id": updated_rental.id,
        "status": updated_rental.status,
        "owner_confirmation": updated_rental.owner_confirmation,
        "tenant_confirmation": updated_rental.tenant_confirmation
    }
