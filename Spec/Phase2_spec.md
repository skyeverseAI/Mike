# Phase 2 — Implementation Spec

## Status
- [ ] Task 1 — Qdrant integrated
- [ ] Task 2 — DocumentSource model + migration
- [ ] Task 3 — Connect local folder to workspace
- [ ] Task 4 — Folder watcher (detection only)
- [ ] Task 5 — FileStatus model + migration

---

## Task 1 — Integrate Qdrant

### docker-compose.yml
- Add qdrant service: image `qdrant/qdrant:latest`, port 6333, named volume `qdrant_data`

### .env / .env.example
- Add `QDRANT_HOST` and `QDRANT_PORT`

### backend/app/core/config.py
- Add `QDRANT_HOST` and `QDRANT_PORT` to Settings

### backend/app/db/qdrant.py
- Create QdrantClient using settings
- `init_qdrant()` — creates collection `documents` if it does not exist
- Collection config: vector size 1024 (bge-m3), cosine distance

### backend/app/main.py
- Call `init_qdrant()` inside FastAPI lifespan on startup

### Verify
- `curl http://localhost:6333/collections` returns ok

---

## Task 2 — DocumentSource Model

### backend/app/models/document_source.py
- `SourceType` enum: `local_folder | google_drive | manual_upload`
- Fields: `id`, `workspace_id` (FK → workspaces), `type`, `path`, `created_at`
- Relationship to Workspace (back_populates)
- Relationship to FileStatus (back_populates)

### backend/app/models/workspace.py
- Add `sources` relationship

### backend/app/schemas/document_source.py
- `DocumentSourceCreate`: type, path
- `DocumentSourceResponse`: id, workspace_id, type, path, created_at

### alembic/env.py
- Import `document_source` model so Alembic detects it

### Migration
- `alembic revision --autogenerate -m "add document_source"`
- `alembic upgrade head`

---

## Task 3 — Connect Local Folder to Workspace

### backend/app/api/routes/sources.py
- `POST /workspaces/{workspace_id}/sources` — saves DocumentSource to DB, returns it
- `GET /workspaces/{workspace_id}/sources` — lists all sources for a workspace
- Both routes: verify workspace belongs to current user

### backend/app/main.py
- Include sources router

### Verify
- POST returns the saved source
- GET lists it

---

## Task 4 — Folder Watcher

### backend/app/services/watcher.py
- `FolderEventHandler` — on file created, check extension (.pdf, .docx, .txt), print `Detected: {filename}`, ignore everything else
- `WatcherManager` — holds the Observer, exposes `watch(source_id, workspace_id, path)` and `start() / stop()`
- Single `watcher_manager` instance

### backend/app/main.py
- On startup: query all `local_folder` DocumentSources from DB, register each with watcher_manager, call `start()`
- On shutdown: call `watcher_manager.stop()`

### Add to requirements.txt
- `watchdog`

### Verify
- Drop a PDF into the watched folder
- Backend logs print: `Detected: contract.pdf`

---

## Task 5 — FileStatus Model

### backend/app/models/file_status.py
- `FileStatusEnum`: `pending | parsing | chunking | embedding | ready | failed`
- Fields: `id`, `workspace_id` (FK), `source_id` (FK → document_sources), `filename`, `filepath`, `status`, `error_message` (nullable), `created_at`, `updated_at`
- Relationship to DocumentSource (back_populates)

### backend/app/schemas/file_status.py
- `FileStatusResponse`: all fields except filepath

### backend/app/api/routes/files.py
- `GET /workspaces/{workspace_id}/files` — lists all FileStatus records for a workspace

### backend/app/main.py
- Include files router

### backend/app/services/watcher.py
- Update `on_created` to create a FileStatus row with status `pending` after printing detection

### alembic/env.py
- Import `file_status` model

### Migration
- `alembic revision --autogenerate -m "add file_status"`
- `alembic upgrade head`

### Verify
- Drop PDF into folder
- `GET /workspaces/{id}/files` returns the file with `status: pending`

---

## Final Checks
- [ ] Qdrant running and collection created
- [ ] DocumentSource saved via API
- [ ] Dropping PDF prints detection in logs
- [ ] FileStatus row created with status: pending
- [ ] All migrations applied: `alembic current` shows head
- [ ] Data survives `docker compose down && docker compose up`
