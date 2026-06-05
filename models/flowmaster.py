from .base import Base
from sqlalchemy.dialects.mysql import TEXT,JSON,BOOLEAN, INTEGER,TIMESTAMP,DECIMAL
from sqlalchemy.dialects.postgresql import ARRAY,UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timedelta
from sqlalchemy import  Uuid



class flow(Base):
    __tablename__="flowmaster"


    number: Mapped[TEXT] = mapped_column(TEXT, nullable=True)
    role: Mapped[TEXT] = mapped_column(TEXT, nullable=True, unique=True)
    service: Mapped[TEXT] = mapped_column(TEXT, nullable=True)
    status: Mapped[TEXT] = mapped_column(TEXT, nullable=True)
    user_data: Mapped[JSON] = mapped_column(JSON, nullable=True)
    created_at: Mapped[TIMESTAMP]= mapped_column(TIMESTAMP, nullable= True,default=datetime.now())
    updated_at: Mapped[TIMESTAMP]= mapped_column(TIMESTAMP, nullable= True)



