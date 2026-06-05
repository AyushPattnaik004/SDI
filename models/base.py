from pydantic import BaseModel
from datetime import datetime, timezone
from sqlalchemy import Uuid, Column
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timedelta
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    id:Mapped[Uuid] = Column(Uuid, primary_key=True)

    class Config:
        arbitrary_types_allowed = True 
