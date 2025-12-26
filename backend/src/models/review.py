from sqlalchemy import Column, SmallInteger, Text, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.connection import Base
import uuid

class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("rental_id", name="uq_review_rental"),)

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rental_id = Column(PG_UUID(as_uuid=True), ForeignKey("rentals.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    author_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    recipient_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    rating = Column(SmallInteger, nullable=False, index=True)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    author = relationship("User", foreign_keys=[author_id], back_populates="reviews_given")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="reviews_received")