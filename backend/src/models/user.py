from sqlalchemy import Column, String, Text, Numeric, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=False)
    avatar_url = Column(String)
    bio = Column(Text)
    rating = Column(Numeric(3, 2), default=5.0, index=True)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    auth = relationship("UserAuth", back_populates="user", uselist=False, cascade="all, delete-orphan")
    owned_items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
    rentals_as_tenant = relationship("Rental", foreign_keys="Rental.tenant_id", back_populates="tenant")
    sent_messages = relationship("Message", back_populates="sender")
    reviews_given = relationship("Review", foreign_keys="Review.author_id", back_populates="author")
    reviews_received = relationship("Review", foreign_keys="Review.recipient_id", back_populates="recipient")
    conversations = relationship("ConversationParticipant", back_populates="user")


class UserAuth(Base):
    __tablename__ = "user_auth"

    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    social_id = Column(String, index=True)
    auth_provider = Column(String, index=True)
    password_hash = Column(String)

    user = relationship("User", back_populates="auth")