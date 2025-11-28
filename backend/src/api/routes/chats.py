from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..dependencies import get_db
from src.queries.orm import Repository
from src.models.item import Item

router = APIRouter(prefix="/chats", tags=["Chats"])

@router.get("/")
async def get_user_conversations(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    repo = Repository(db)
    convs = await repo.conversations.get_user_conversations(user_id)
    return convs

@router.post("/start")
async def start_conversation(
    item_id: UUID,
    current_user_id: UUID,  
    db: AsyncSession = Depends(get_db)
):
    repo = Repository(db)
    item = await repo.items.get_by_id(Item, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    
    user_ids = [current_user_id, item.owner_id]
    conv = await repo.conversations.get_or_create_by_item(item_id, user_ids)
    return conv

@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    repo = Repository(db)
    messages = await repo.messages.get_messages(conversation_id)
    return messages

@router.post("/{conversation_id}/messages")
async def send_message(
    conversation_id: UUID,
    text: str,
    sender_id: UUID,  # из токена
    db: AsyncSession = Depends(get_db)
):
    repo = Repository(db)
    msg = await repo.messages.create_message(conversation_id, sender_id, text)
    return msg