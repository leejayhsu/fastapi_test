from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class BrandModel(Base):
    __tablename__ = "brand"
    # only for postgres
    # uuid = Column(
    #     UUID(as_uuid=True), default=uuid4, primary_key=True, unique=True, nullable=False
    # )
    uuid = Column(
        "uuid", Text(length=36), default=lambda: str(uuid4()), primary_key=True
    )
    kyc_vendor = Column(String(20))
    # brand_id = Column(UUID(as_uuid=True), unique=True)
    brand_id = Column(
        "brand_id", Text(length=36), default=lambda: str(uuid4()), unique=True
    )
    date_created = Column(DateTime, default=datetime.now(timezone.utc))
    date_updated = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
