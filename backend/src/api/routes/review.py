from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.api.dependencies import DatabaseDep, CurrentUser
from src.queries.reviews import create_review, get_reviews_for_user, ReviewCreate, ReviewResponse
from ..dependencies import get_db

router = APIRouter()

@router.post("/", response_model=ReviewResponse)
async def create_user_review(
    review: ReviewCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Создать отзыв на пользователя (после аренды)"""
    try:
        return await create_review(db, current_user, review)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{user_id}", response_model=list[ReviewResponse])
async def get_user_reviews(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Получить все отзывы о пользователе"""
    return await get_reviews_for_user(db, user_id)