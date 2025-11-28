from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.connection import get_db

def get_db_dependency():
    return Depends(get_db)