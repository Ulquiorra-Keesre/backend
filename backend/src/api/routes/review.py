# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from uuid import UUID
# from pydantic import BaseModel, Field

# from src.api.dependencies import DatabaseDep, CurrentUser
# from src.queries import Repository
# from src.models.rental import Rental
# from src.models.review import Review
# from src.models.item import Item

# router = APIRouter(prefix="/reviews", tags=["Reviews"])


# class ReviewCreate(BaseModel):
#     rental_id: UUID
#     recipient_id: UUID
#     rating: int = Field(ge=1, le=5)
#     comment: str = ""


# @router.post("/")
# async def create_review(review: ReviewCreate, current_user: CurrentUser, db: DatabaseDep):
    
#     repo = Repository(db)

#     rental = await repo.rentals.get_by_id(review.rental_id)
#     if not rental:
#         raise HTTPException(status.HTTP_404_NOT_FOUND, "Rental not found")

#     if rental.tenant_id != current_user:
#         raise HTTPException(status.HTTP_403_FORBIDDEN, "Only tenant can leave a review")

#     item = await repo.items.get_by_id(rental.item_id)
#     if not item or item.owner_id != review.recipient_id:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, "Recipient must be the owner of the rented item")

#     existing = await repo.session.execute(
#         select(Review).where(Review.rental_id == review.rental_id)
#     )
#     if existing.scalar_one_or_none():
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, "Review already exists for this rental")

#     review = await repo.reviews.create(
#         Review,
#         rental_id=review.rental_id,
#         author_id=current_user,
#         recipient_id=review.recipient_id,
#         rating=review.rating,
#         comment=review.comment
#     )
#     return review

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