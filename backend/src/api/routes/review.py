from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel, Field

from src.api.dependencies import DatabaseDep, CurrentUser
from src.queries import Repository
from src.models.rental import Rental
from src.models.review import Review
from src.models.item import Item

router = APIRouter(prefix="/reviews", tags=["Reviews"])


class ReviewCreate(BaseModel):
    rental_id: UUID
    recipient_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str = ""


@router.post("/")
async def create_review(review: ReviewCreate, current_user: CurrentUser, db: DatabaseDep):
    
    repo = Repository(db)

    rental = await repo.rentals.get_by_id(review.rental_id)
    if not rental:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rental not found")

    if rental.tenant_id != current_user:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only tenant can leave a review")

    item = await repo.items.get_by_id(rental.item_id)
    if not item or item.owner_id != review.recipient_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Recipient must be the owner of the rented item")

    existing = await repo.session.execute(
        select(Review).where(Review.rental_id == review.rental_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Review already exists for this rental")

    review = await repo.reviews.create(
        Review,
        rental_id=review.rental_id,
        author_id=current_user,
        recipient_id=review.recipient_id,
        rating=review.rating,
        comment=review.comment
    )
    return review