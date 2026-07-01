import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class SourceType(str, enum.Enum):
    local_folder = "local_folder"
    google_drive = "google_drive"
    manual_upload = "manual_upload"


class DocumentSource(Base):
    __tablename__ = "document_sources"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False)
    type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="sources")
    files: Mapped[list["FileStatus"]] = relationship("FileStatus", back_populates="source")

    