from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from src.queries import Repository 
from src.models.user import User

from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    email: str
    phone: Optional[str] = None
    full_name: str
    password: str  

class UserResponse(BaseModel):
    id: UUID
    email: str
    phone: Optional[str]
    full_name: str
    # avatar_url: Optional[str]
    # rating: float
    created_at: datetime

    class Config:
        from_attributes = True  


async def create_user(db: AsyncSession, user: UserCreate) -> UserResponse:
    """Создать пользователя с хэшированием пароля"""
    from src.utils.security import get_password_hash
    repo = Repository(db)

    existing = await repo.users.get_by_email(user.email)
    if existing:
        raise ValueError("Email already registered")

    user_data = {
        "email": user.email,
        "phone": user.phone,
        "full_name": user.full_name,
    }
    auth_data = {
        "password_hash": get_password_hash(user.password)
    }

    db_user = await repo.users.create_with_auth(user_data, auth_data)
    return UserResponse.model_validate(db_user)

async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[UserResponse]:
    repo = Repository(db)
    user = await repo.users.get_by_id(User, user_id)
    return UserResponse.model_validate(user) if user else None

async def get_user_profile(db: AsyncSession, user_id: UUID) -> Optional[UserResponse]:
    """Получить профиль (без паролей и приватных данных)"""
    return await get_user_by_id(db, user_id)