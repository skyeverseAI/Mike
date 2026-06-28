from pydantic import BaseModel
from datetime import datetime

class WorkspaceCreate(BaseModel):
    name: str

class WorkspaceResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    created_at: datetime

    class Config:
        from_attributes = True
