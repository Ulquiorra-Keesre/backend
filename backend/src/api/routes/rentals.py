from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..dependencies import get_db

from src.api.dependencies import DatabaseDep, CurrentUser
from src.queries.rentals import (
    create_rental, 
    get_user_rentals, 
    confirm_rental,
    RentalCreate, 
    RentalResponse
)

router = APIRouter()

@router.post("/", response_model=RentalResponse)
async def create_new_rental(
    rental: RentalCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Создать новую аренду (арендатор)"""
    try:
        # Устанавка арендатора как текущего пользователя
        rental.tenant_id = current_user
        return await create_rental(db, rental)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/me", response_model=list[RentalResponse])
async def get_my_rentals(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    """Получить все мои аренды (как арендатор или владелец)"""
    return await get_user_rentals(db, current_user)

@router.post("/{rental_id}/confirm", response_model=RentalResponse)
async def confirm_rental_endpoint(rental_id: UUID, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    try:
        return await confirm_rental(db, rental_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))