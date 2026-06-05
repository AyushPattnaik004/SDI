from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

class Base(BaseModel):
    id: Optional[UUID] = None

    class Config:
        arbitrary_types_allowed=True


