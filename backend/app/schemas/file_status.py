from pydantic import BaseModel
from datetime import datetime
from app.models.file_status import FileStatusEnum

class FileStatusResponse(BaseModel):
    id: str
    workspace_id: str
    source_id: str
    filename: str
    status: FileStatusEnum
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
