from .base import Base
from sqlalchemy.dialects.mysql import TEXT,JSON,BOOLEAN, INTEGER,TIMESTAMP,DECIMAL
from sqlalchemy.dialects.postgresql import ARRAY,UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timedelta
from sqlalchemy import  Uuid



class profile(Base):
    __tablename__="profile"


    name: Mapped[TEXT] = mapped_column(TEXT, nullable=True)
    number: Mapped[TEXT] = mapped_column(TEXT, nullable=True)
    email: Mapped[TEXT] = mapped_column(TEXT, nullable=True, unique=True)
    gender: Mapped[TEXT] = mapped_column(TEXT, nullable=True)
    age: Mapped[INTEGER] = mapped_column(INTEGER,nullable=True)
    course: Mapped[TEXT] = mapped_column(TEXT, nullable=True)
    is_sponsored: Mapped[BOOLEAN] = mapped_column(BOOLEAN, nullable=True)
    qualification: Mapped[TEXT] = mapped_column(TEXT, nullable=True)
    branch: Mapped[TEXT] = mapped_column(TEXT, nullable=True)
    twelveth_p: Mapped[TEXT] = mapped_column(TEXT, nullable=True)
    tenth_p: Mapped[TEXT] = mapped_column(TEXT, nullable=True)
    created_at: Mapped[TIMESTAMP]= mapped_column(TIMESTAMP, nullable= True,default=datetime.now())
    updated_at: Mapped[TIMESTAMP]= mapped_column(TIMESTAMP, nullable= True)



