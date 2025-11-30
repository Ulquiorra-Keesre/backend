from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from src.api.dependencies import DatabaseDep, CurrentUser  
from src.queries import Repository
from src.models.item import Item
from src.models.conversation import ConversationParticipant

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.get("/")
async def get_user_conversations(
    current_user: CurrentUser, 
    db: DatabaseDep
):
    """Получить все беседы текущего пользователя"""
    repo = Repository(db)
    convs = await repo.conversations.get_user_conversations(current_user)
    return convs


@router.post("/start")
async def start_conversation(
    item_id: UUID,
    current_user: CurrentUser,  
    db: DatabaseDep
):
    """Начать чат по предмету (если ещё не существует)"""
    repo = Repository(db)
    
    item = await repo.items.get_by_id(Item, item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    
    if item.owner_id == current_user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot start chat with yourself")
    
    user_ids = [current_user, item.owner_id]
    conv = await repo.conversations.get_or_create_by_item(item_id, user_ids)
    return conv


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: UUID,
    current_user: CurrentUser,
    db: DatabaseDep
):
    """Получить сообщения в беседе (только если пользователь — участник)"""
    repo = Repository(db)
    
    participant = await repo.session.execute(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user,
            ConversationParticipant.is_active.is_(True)
        )
    )
    if not participant.scalar_one_or_none():
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not a participant of this conversation")
    
    messages = await repo.messages.get_messages_in_conversation(conversation_id)
    return messages


@router.post("/{conversation_id}/messages")
async def send_message(
    conversation_id: UUID,
    text: str,
    current_user: CurrentUser,  
    db: DatabaseDep
):
    """Отправить сообщение в беседу"""
    repo = Repository(db)
    
    participant = await repo.session.execute(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user,
            ConversationParticipant.is_active.is_(True)
        )
    )
    if not participant.scalar_one_or_none():
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You cannot send messages to this conversation")
    
    msg = await repo.messages.create_message(conversation_id, current_user, text)
    return msg