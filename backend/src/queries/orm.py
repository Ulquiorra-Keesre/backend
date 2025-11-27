from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from uuid import UUID

from .core import DatabaseManager
from ..models.user import User, UserAuth
from ..models.item import Item, ItemImage
from ..models.category import Category
from ..models.rental import Rental
from ..models.conversation import Conversation, ConversationParticipant
from ..models.message import Message

# ------------------ UserRepository ------------------
class UserRepository(DatabaseManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = User

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.get_by_field(User, "email", email)

    async def get_by_phone(self, phone: str) -> Optional[User]:
        return await self.get_by_field(User, "phone", phone)

    async def create_with_auth(self, user_data: dict, auth_data: dict) -> User:
        try:
            user = User(**user_data)
            self.session.add(user)
            await self.session.flush()
            auth_data["user_id"] = user.id
            user_auth = UserAuth(**auth_data)
            self.session.add(user_auth)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as e:
            await self.session.rollback()
            raise

# ------------------ ItemRepository ------------------
class ItemRepository(DatabaseManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = Item

    async def get_available_items_near(
        self, lat: float, lon: float, radius_km: float = 5.0
    ) -> List[Item]:
        delta = radius_km / 111.0  # approx degrees per km
        stmt = (
            select(Item)
            .where(
                Item.is_available.is_(True),
                Item.latitude.between(lat - delta, lat + delta),
                Item.longitude.between(lon - delta, lon + delta),
            )
            .options(selectinload(Item.images))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_owner(self, owner_id: UUID) -> List[Item]:
        stmt = select(Item).where(Item.owner_id == owner_id).options(selectinload(Item.images))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_with_images(self, item_data: dict, image_urls: List[str]) -> Item:
        try:
            item = Item(**item_data)
            self.session.add(item)
            await self.session.flush()

            images = [
                ItemImage(item_id=item.id, image_url=url, order_index=i)
                for i, url in enumerate(image_urls)
            ]
            self.session.add_all(images)
            await self.session.commit()
            await self.session.refresh(item)
            return item
        except Exception as e:
            await self.session.rollback()
            raise

# ------------------ ConversationRepository ------------------
class ConversationRepository(DatabaseManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_or_create_conversation(self, item_id: UUID, user_ids: List[UUID]) -> Conversation:
        # Проверим, существует ли беседа по item_id
        stmt = select(Conversation).where(Conversation.item_id == item_id)
        result = await self.session.execute(stmt)
        conv = result.scalar_one_or_none()

        if not conv:
            conv = Conversation(item_id=item_id)
            self.session.add(conv)
            await self.session.flush()

            # Добавляем участников
            participants = [
                ConversationParticipant(
                    conversation_id=conv.id,
                    user_id=user_id,
                    is_active=True
                )
                for user_id in user_ids
            ]
            self.session.add_all(participants)
            await self.session.commit()
            await self.session.refresh(conv)
        return conv

    async def get_user_conversations(self, user_id: UUID) -> List[Conversation]:
        stmt = (
            select(Conversation)
            .join(ConversationParticipant)
            .where(
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.is_active.is_(True)
            )
            .order_by(Conversation.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

# ------------------ MessageRepository ------------------
class MessageRepository(DatabaseManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = Message

    async def create_message(
        self, conversation_id: UUID, sender_id: UUID, text: str, message_type: str = "text"
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            message_text=text,
            message_type=message_type,
            is_read=False
        )
        self.session.add(message)

        # Обновляем updated_at у conversation
        await self.session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(updated_at=func.now())
        )

        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_messages_in_conversation(
        self, conversation_id: UUID, limit: int = 50, offset: int = 0
    ) -> List[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

# ------------------ RentalRepository ------------------
class RentalRepository(DatabaseManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = Rental

    async def get_active_rentals_for_user(self, user_id: UUID) -> List[Rental]:
        stmt = select(Rental).where(
            or_(Rental.tenant_id == user_id, Rental.item_id.in_(
                select(Item.id).where(Item.owner_id == user_id)
            )),
            Rental.status.in_(["confirmed", "active"])
        ).options(
            selectinload(Rental.item).selectinload(Item.images),
            selectinload(Rental.item).selectinload(Item.owner)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

# ------------------ CategoryRepository ------------------
class CategoryRepository(DatabaseManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = Category

    async def get_all_with_children(self) -> List[Category]:
        stmt = select(Category)
        result = await self.session.execute(stmt)
        return result.scalars().all()

# ------------------ Main Repository Facade ------------------
class Repository:
    def __init__(self, session: AsyncSession):
        self.users = UserRepository(session)
        self.items = ItemRepository(session)
        self.conversations = ConversationRepository(session)
        self.messages = MessageRepository(session)
        self.rentals = RentalRepository(session)
        self.categories = CategoryRepository(session)