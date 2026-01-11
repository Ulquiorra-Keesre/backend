from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import DatabaseDep  
from src.queries import Repository               
from src.models.category import Category

router = APIRouter()

@router.get("/")
async def list_categories(db: DatabaseDep):  
    repo = Repository(db)
    categories = await repo.categories.get_all_with_children()
    return categories