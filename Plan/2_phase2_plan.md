# Phase 2 — Document Ingestion

## Goal
When a user drops a file into a workspace folder, it gets detected, processed,
and stored in Qdrant — ready to be queried. No chat yet.

## Stack Additions
- Qdrant (vector database)
- watchdog (folder monitoring)
- LangChain (chunking)
- bge-m3 via Ollama (embeddings)
- pypdf (PDF parsing)
- python-docx (DOCX parsing)
- FastAPI BackgroundTasks (async pipeline)

## New Models
```
Workspace
 └── DocumentSource  (local_folder | google_drive* | manual_upload*)
      └── FileStatus  (pending → parsing → chunking → embedding → ready | failed)

* future
```

## Project Structure Additions
```
backend/app/
├── models/
│   ├── document_source.py
│   └── file_status.py
├── schemas/
│   ├── document_source.py
│   └── file_status.py
├── api/routes/
│   ├── sources.py
│   └── files.py
├── db/
│   └── qdrant.py
└── services/
    ├── watcher.py
    └── pipeline.py          ← Phase 2 stub only
```

## Task Breakdown

### Task 1 — Integrate Qdrant
- Add Qdrant to docker-compose.yml
- Create qdrant.py client in backend
- Verify connection on app startup
- One collection: `documents` (all workspaces, filtered by metadata)

### Task 2 — DocumentSource Model
- Fields: id, workspace_id, type (enum), path, created_at
- Type enum: local_folder | google_drive | manual_upload
- Alembic migration

### Task 3 — Connect Local Folder to Workspace
- POST /workspaces/{id}/sources
- Body: { type, path }
- Saves to DB. No watching yet.
- GET /workspaces/{id}/sources to list sources

### Task 4 — Folder Watcher
- watchdog monitors all local_folder sources on startup
- On file created: print "Detected: {filename}"
- Accepted types: .pdf, .docx, .txt
- Ignored types: silently skipped
- Watcher restarts with latest sources on each app startup

### Task 5 — FileStatus Model
- Fields: id, workspace_id, source_id, filename, filepath, status, error_message, created_at, updated_at
- Status enum: pending | parsing | chunking | embedding | ready | failed
- Alembic migration
- GET /workspaces/{id}/files to list statuses

## Key Design Decisions
- One Qdrant collection for all workspaces, workspace_id stored as metadata
- BackgroundTasks over Celery (single user, no queue needed yet)
- Detection and processing are separate concerns — Task 4 proves detection only
- error_message stored on FileStatus so failures are debuggable

## Done When
- [ ] Qdrant runs in Docker and backend connects to it
- [ ] User can connect a local folder to a workspace
- [ ] Dropping a PDF into the folder prints "Detected: contract.pdf"
- [ ] FileStatus row is created on detection with status: pending
- [ ] All new models have Alembic migrations
- [ ] Data survives Docker restart
