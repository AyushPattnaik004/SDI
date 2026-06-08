from .base import Base
from sqlalchemy.dialects.postgresql import TEXT, UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import uuid

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name: Mapped[str] = mapped_column(TEXT, nullable=True)
    sector: Mapped[str] = mapped_column(TEXT, nullable=True)
    city: Mapped[str] = mapped_column(TEXT, nullable=True)
    state: Mapped[str] = mapped_column(TEXT, nullable=True)
    tier: Mapped[str] = mapped_column(TEXT, nullable=True)
    skills: Mapped[str] = mapped_column(TEXT, nullable=True)
    website: Mapped[str] = mapped_column(TEXT, nullable=True)
    hr_contact: Mapped[str] = mapped_column(TEXT, nullable=True)
    notes: Mapped[str] = mapped_column(TEXT, nullable=True)
    mobile_no: Mapped[str] = mapped_column(TEXT, nullable=True)
    gstin: Mapped[str] = mapped_column(TEXT, nullable=True)
    osector: Mapped[str] = mapped_column(TEXT, nullable=True)
    gstno: Mapped[str] = mapped_column(TEXT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), onupdate=datetime.now, nullable=True)

