from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..dependencies import get_db
from ...queries.orm import Repository

router = APIRouter(prefix="/rentals", tags=["Rentals"])

@router.get("/me")
async def get_my_rentals(
    user_id: UUID,  # из токена
    db: AsyncSession = Depends(get_db)
):
    repo = Repository(db)
    rentals = await repo.rentals.get_active_for_user(user_id)
    return rentals