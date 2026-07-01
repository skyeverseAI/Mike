from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.workspace import Workspace
from app.models.file_status import FileStatus
from app.schemas.file_status import FileStatusResponse

router = APIRouter(prefix="/workspaces", tags=["files"])

@router.get("/{workspace_id}/files", response_model=list[FileStatusResponse])
def list_files(workspace_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ws = db.query(Workspace).filter(Workspace.id == workspace_id, Workspace.owner_id == user.id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return db.query(FileStatus).filter(FileStatus.workspace_id == workspace_id).all()
