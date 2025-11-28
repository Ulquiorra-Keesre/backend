from sqlalchemy import Column, String, Text, Numeric, Boolean, DateTime, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base
import uuid

class Item(Base):
    __tablename__ = "items"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(PG_UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    price_per_hour = Column(Numeric(10, 2))
    price_per_day = Column(Numeric(10, 2))
    address = Column(String, nullable=False)
    latitude = Column(Numeric(10, 7), index=True)
    longitude = Column(Numeric(10, 7), index=True)
    is_available = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_items")
    category = relationship("Category", back_populates="items")
    images = relationship("ItemImage", back_populates="item", cascade="all, delete-orphan")
    rentals = relationship("Rental", back_populates="item")
    conversations = relationship("Conversation", back_populates="item")


class ItemImage(Base):
    __tablename__ = "item_images"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(PG_UUID(as_uuid=True), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String, nullable=False)
    order_index = Column(Integer, index=True)

    item = relationship("Item", back_populates="images")