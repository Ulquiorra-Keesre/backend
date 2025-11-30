from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..dependencies import get_db
from src.queries.orm import Repository
from src.models.user import User
from src.api.dependencies import CurrentUser, DatabaseDep
from src.queries.items import ItemCreate

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}")
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = Repository(db)
    user = await repo.users.get_by_id(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}/items")
async def get_user_items(user_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = Repository(db)
    items = await repo.items.get_by_owner(user_id)
    return items

@router.get("/{user_id}/reviews")
async def get_user_reviews(user_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = Repository(db)
    reviews = await repo.reviews.get_reviews_about_user(user_id)
    return reviews

@router.post("/items")
async def create_item(
    item_data: ItemCreate,
    current_user: CurrentUser,  # ← UUID
    db: DatabaseDep
):
    item_data.owner_id = current_user
    item = await create_item(db, item_data)
    return item