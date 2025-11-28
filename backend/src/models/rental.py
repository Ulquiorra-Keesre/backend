from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base
import uuid

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(PG_UUID(as_uuid=True), ForeignKey("items.id", ondelete="RESTRICT"), nullable=False, index=True)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    status = Column(String, index=True)
    total_price = Column(Numeric(10, 2), nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=False)
    owner_confirmation = Column(Boolean, default=False)
    tenant_confirmation = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))

    # Связи
    item = relationship("Item", back_populates="rentals")
    tenant = relationship("User", foreign_keys=[tenant_id], back_populates="rentals_as_tenant")