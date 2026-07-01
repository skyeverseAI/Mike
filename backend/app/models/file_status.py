import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class FileStatusEnum(str, enum.Enum):
    pending = "pending"
    parsing = "parsing"
    chunking = "chunking"
    embedding = "embedding"
    ready = "ready"
    failed = "failed"

class FileStatus(Base):
    __tablename__ = "file_statuses"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(String, ForeignKey("document_sources.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    filepath: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[FileStatusEnum] = mapped_column(Enum(FileStatusEnum), nullable=False, default=FileStatusEnum.pending)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    source: Mapped["DocumentSource"] = relationship("DocumentSource", back_populates="files")
