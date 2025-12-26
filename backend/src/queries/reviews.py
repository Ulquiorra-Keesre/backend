from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from src.models.rental import Rental

from src.queries import Repository
from src.models.review import Review

from pydantic import BaseModel, Field

class ReviewCreate(BaseModel):
    rental_id: UUID
    recipient_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str = ""

class ReviewResponse(BaseModel):
    id: UUID
    author_id: UUID
    recipient_id: UUID
    rating: int
    comment: str
    created_at: str

    class Config:
        from_attributes = True

async def create_review(db: AsyncSession, author_id: UUID, review: ReviewCreate) -> ReviewResponse:
    repo = Repository(db)

    # Проверка аренды
    rental = await repo.rentals.get_by_id(Rental, review.rental_id)  
    if not rental or rental.tenant_id != author_id:
        raise ValueError("Invalid rental or unauthorized")

    # Проверка, не существует ли уже отзыв
    existing = await repo.reviews.get_by_field(Review, "rental_id", review.rental_id)
    if existing:
        raise ValueError("Review already exists")

    review_data = review.dict()
    review_data["author_id"] = author_id
    db_review = await repo.reviews.create(Review, **review_data)
    return ReviewResponse.model_validate(db_review)

async def get_reviews_for_user(db: AsyncSession, user_id: UUID) -> List[ReviewResponse]:
    repo = Repository(db)
    reviews = await repo.reviews.get_reviews_about_user(user_id)
    return [ReviewResponse.model_validate(r) for r in reviews]