import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Table, func, select
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship
from src.db.base import Base
from src.db.registration_model import RegistrationModel
from src.db.speaker_model import SpeakerModel

_session_speaker_assoc = Table(
    "session_speaker",
    Base.metadata,
    Column("session_id", UUID, ForeignKey("content.session.id")),
    Column("speaker_id", UUID, ForeignKey("content.speaker.id")),
    schema="content",
)

class SessionModel(Base):
    __tablename__ = "session"
    __table_args__ = {"schema": "content"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    track_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content.track.id"))
    title: Mapped[str] = mapped_column()
    abstract: Mapped[str | None] = mapped_column()
    starts_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    capacity: Mapped[int | None] = mapped_column()
    track = relationship("TrackModel", lazy="noload")
    
    speakers: Mapped[list[SpeakerModel]] = relationship(
        secondary=_session_speaker_assoc, lazy="noload", viewonly=True
    )

    registered: Mapped[int] = column_property(
        select(func.count(RegistrationModel.id))
        .where(
            RegistrationModel.session_id == id,
            RegistrationModel.status == "confirmed",
        )
        .correlate_except(RegistrationModel)
        .scalar_subquery()
    )
