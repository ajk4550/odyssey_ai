from sqlalchemy import Column, Integer, JSON, DateTime, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase
from datetime import timezone, datetime
from models.enums import TripStatus

class Base(DeclarativeBase):
    pass

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_input = Column(JSON)
    status = Column(SAEnum(TripStatus), nullable=False, default=TripStatus.pending)
    result = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
