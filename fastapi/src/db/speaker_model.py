import uuid
from sqlalchemy.orm import Mapped, mapped_column
from src.db.base import Base

class SpeakerModel(Base):
    __tablename__ = "speaker"
    __table_args__ = {"schema": "content"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    affiliation: Mapped[str | None] = mapped_column()
