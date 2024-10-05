from pydantic import BaseModel
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

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
