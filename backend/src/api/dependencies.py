# backend/src/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID

from src.database.connection import get_db
from src.utils.security import verify_token  
from src.queries.users import get_user_by_id

security = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UUID:
    """
    Возвращает UUID текущего авторизованного пользователя.
    """
    user_id_str = verify_token(credentials.credentials)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


DatabaseDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[UUID, Depends(get_current_user)]

# DatabaseDep = Depends(get_db)
# CurrentUser = Depends(get_current_user)