import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Workspace(Base):
    __tablename__ = "workspaces"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner: Mapped["User"] = relationship("User", back_populates="workspaces")
    sources: Mapped[list["DocumentSource"]] = relationship("DocumentSource", back_populates="workspace")