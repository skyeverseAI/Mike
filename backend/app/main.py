
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, workspaces, sources, files
from app.db.qdrant import init_qdrant
from app.db.session import SessionLocal
from app.models import user, workspace
from app.models import file_status
from app.models.document_source import DocumentSource, SourceType
from app.services.watcher import watcher_manager
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_qdrant()
    db = SessionLocal()
    try:
        local_sources = db.query(DocumentSource).filter(DocumentSource.type == SourceType.local_folder).all()
        print(f"Found {len(local_sources)} local sources")
        for source in local_sources:
            watcher_manager.watch(source.id, source.workspace_id, source.path)
    finally:
        db.close()
    watcher_manager.start()
    yield
    watcher_manager.stop()
   


app = FastAPI(title="Mike Legal AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(workspaces.router)
app.include_router(sources.router)
app.include_router(files.router)

@app.get("/health")
def health():
    return {"status": "ok"}

