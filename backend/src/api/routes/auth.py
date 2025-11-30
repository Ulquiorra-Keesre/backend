from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.api.dependencies import DatabaseDep
from src.models.auth import UserRegister, UserLogin, Token
from src.models.user import User, UserAuth
from src.queries import Repository
from src.utils.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Token)
async def register(user: UserRegister, db: DatabaseDep):
    repo = Repository(db)

    # Проверка: email 
    existing = await repo.users.get_by_email(user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Создаём пользователя
    user_data = {
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
    }
    auth_data = {
        "password_hash": get_password_hash(user.password)
    }

    db_user = await repo.users.create_with_auth(user_data, auth_data)

    # Создаём токен
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: DatabaseDep):

    repo = Repository(db)
    user = await repo.users.get_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(UserAuth).where(UserAuth.user_id == user.id))
    user_auth = result.scalar_one_or_none()

    if not user_auth or not verify_password(credentials.password, user_auth.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")