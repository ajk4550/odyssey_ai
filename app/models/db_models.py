import enum
from sqlalchemy import Column, Integer, String, JSON, DateTime, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase
from datetime import timezone, datetime

class Base(DeclarativeBase):
    pass

class TripStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_input = Column(JSON)
    status = Column(SAEnum(TripStatus), nullable=False, default=TripStatus.pending)
    result = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
