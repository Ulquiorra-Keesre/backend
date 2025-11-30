from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.queries import Repository
from src.models.category import Category
from typing import Optional

from pydantic import BaseModel
from uuid import UUID

class CategoryResponse(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[UUID]

    class Config:
        from_attributes = True

async def get_all_categories(db: AsyncSession) -> List[CategoryResponse]:
    repo = Repository(db)
    categories = await repo.categories.get_all_with_children()
    return [CategoryResponse.model_validate(cat) for cat in categories]