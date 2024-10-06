from pydantic import BaseModel
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Event(BaseModel):
    customer_id: str
    event_name: str
    properties: Dict[str, Any]
    idempotency_id: str
    time_created: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None,
            datetime: lambda v: v.isoformat() if v is not None else None
        }

class EventStatus(Base):
    __tablename__ = 'event_status'

    id = Column(Integer, primary_key=True)
    event_id = Column(String, unique=True, nullable=False)  # Идентификатор события
    event_data = Column(JSON, nullable=False)  # Данные события в формате JSON
    status = Column(String, nullable=False, default='new')  # Статус события
    attempts = Column(Integer, default=0)  # Количество попыток отправки
    last_error = Column(Text, nullable=True)  # Текст последней ошибки
    created_at = Column(DateTime, default=datetime.utcnow)  # Время создания записи
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_event_status_status', 'status'),
        Index('ix_event_status_attempts', 'attempts'),
    )
