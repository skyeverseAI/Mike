from pydantic import BaseModel
from datetime import datetime
from app.models.document_source import SourceType

class DocumentSourceCreate(BaseModel):
    type: SourceType
    path: str

class DocumentSourceResponse(BaseModel):
    id: str
    workspace_id: str
    type: SourceType
    path: str
    created_at: datetime

    class Config:
        from_attributes = True
    