from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.workspace import Workspace
from app.models.document_source import DocumentSource
from app.schemas.document_source import DocumentSourceCreate, DocumentSourceResponse  

router = APIRouter(prefix="/workspaces", tags=["sources"])

@router.post("/{workspace_id}/sources", response_model=DocumentSourceResponse)
def add_source(workspace_id: str, body: DocumentSourceCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ws = db.query(Workspace).filter(Workspace.id == workspace_id, Workspace.owner_id == user.id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    source = DocumentSource(workspace_id=ws.id, type=body.type, path=body.path)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source

@router.get("/{workspace_id}/sources", response_model=list[DocumentSourceResponse])
def list_sources(workspace_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ws = db.query(Workspace).filter(Workspace.id == workspace_id, Workspace.owner_id == user.id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return db.query(DocumentSource).filter(DocumentSource.workspace_id == workspace_id).all()