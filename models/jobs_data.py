from .base import Base
from sqlalchemy.dialects.postgresql import (
    VARCHAR,
    TEXT,
    UUID,
    JSON,
    TIMESTAMP,
    INTEGER,
    DATE,
    BIGINT,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from datetime import datetime
import uuid


class Jobs(Base):

    __tablename__ = "jobs"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    job_type: Mapped[VARCHAR] = mapped_column(VARCHAR(100), nullable=False)
    job_specialization: Mapped[VARCHAR] = mapped_column(VARCHAR(150), nullable=False)
    job_description: Mapped[TEXT] = mapped_column(TEXT, nullable=False)

    # Location
    location: Mapped[VARCHAR] = mapped_column(VARCHAR(100), nullable=False)
    custom_location: Mapped[VARCHAR] = mapped_column(VARCHAR(255), nullable=True)

    # Salary
    salary_min: Mapped[INTEGER] = mapped_column(INTEGER, nullable=False)
    salary_max: Mapped[INTEGER] = mapped_column(INTEGER, nullable=False)
    

    # Requirements
    experience: Mapped[VARCHAR] = mapped_column(VARCHAR(255), nullable=True)
    qualification: Mapped[VARCHAR] = mapped_column(VARCHAR(255), nullable=True)
    age: Mapped[VARCHAR] = mapped_column(VARCHAR(50), nullable=True)

    # Joining Details
    joining_date_option: Mapped[VARCHAR] = mapped_column(VARCHAR(50), nullable=False)
    joining_date: Mapped[DATE] = mapped_column(DATE, nullable=True)

    headcount: Mapped[INTEGER] = mapped_column(INTEGER, default=1, nullable=True)
    gender_preference: Mapped[VARCHAR] = mapped_column(VARCHAR(50), nullable=True)
    additional_notes: Mapped[TEXT] = mapped_column(TEXT, nullable=True)
    sdi_introduction_letter: Mapped[TEXT] = mapped_column(TEXT, nullable=True)

    # Shortlisting
    shortlisted_profile: Mapped[JSON] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP, default=datetime.now, nullable=False
    )
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False
    )
