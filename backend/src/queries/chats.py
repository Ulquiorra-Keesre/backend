# src/queries/chats.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.queries import Repository
from src.models.message import Message
from src.models.conversation import Conversation
from src.models.item import Item

from pydantic import BaseModel

class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    message_text: str
    created_at: str

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: UUID
    item_id: UUID
    updated_at: str

    class Config:
        from_attributes = True

async def start_conversation(
    db: AsyncSession, item_id: UUID, current_user_id: UUID
) -> ConversationResponse:
    repo = Repository(db)
    item = await repo.items.get_by_id(Item, item_id)
    if not item:
        raise ValueError("Item not found")
    user_ids = [current_user_id, item.owner_id]
    conv = await repo.conversations.get_or_create_conversation(item_id, user_ids)
    return ConversationResponse.model_validate(conv)

async def get_conversation_messages(
    db: AsyncSession, conversation_id: UUID, limit: int = 50
) -> List[MessageResponse]:
    repo = Repository(db)
    messages = await repo.messages.get_messages_in_conversation(conversation_id, limit=limit)
    return [MessageResponse.model_validate(m) for m in messages]

async def send_message(
    db: AsyncSession, conversation_id: UUID, sender_id: UUID, text: str
) -> MessageResponse:
    repo = Repository(db)
    msg = await repo.messages.create_message(conversation_id, sender_id, text)
    return MessageResponse.model_validate(msg)