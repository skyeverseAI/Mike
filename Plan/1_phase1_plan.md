\# Phase 1 — Platform Foundation

## Goal
Build the application skeleton that every future feature will sit on top of.

## Stack
- Backend: FastAPI (Python)
- Frontend: Next.js
- Database: PostgreSQL + Alembic
- Auth: JWT
- Infrastructure: Docker + Docker Compose

## Pre-Flight Check (30 min, throwaway)
Verify AI stack works before building infrastructure around it.
```
ollama serve
ollama run qwen2.5:14b "hello"
ollama pull bge-m3 → test embeddings API
docker run qdrant/qdrant → hit localhost:6333
```

## Project Structure
```
mike-legal-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   └── workspaces.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── workspace.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   └── workspace.py
│   │   └── main.py
│   ├── alembic/
│   │   └── versions/
│   ├── alembic.ini
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── dashboard/page.tsx
│   │   └── layout.tsx
│   ├── components/
│   ├── lib/
│   │   └── api.ts
│   ├── Dockerfile
│   └── package.json
│
├── Plan/
├── docker-compose.yml
├── .env.example
├── .env
└── .gitignore
```

## Workspace Definition
An isolated AI knowledge space owned by a user.
Contains: document sources, indexed documents, chats, memory, settings.

```
User
 └── Workspace (many per user)
      ├── DocumentSource (local_folder | google_drive | manual)
      ├── Document
      ├── ChatSession
      └── WorkspaceSettings
```

## Build Order
1. Git repo + .gitignore + .env.example
2. Docker Compose + PostgreSQL
3. FastAPI skeleton + /health endpoint
4. SQLAlchemy models + first Alembic migration
5. JWT auth (register, login)
6. Workspace CRUD
7. Next.js frontend (register, login, dashboard)

## Done When
- [x] `docker compose up` starts all services cleanly
- [x] `GET /health` returns `{"status": "ok"}`
- [ ] User can register
- [ ] User can login
- [ ] User can create, list, delete workspaces
- [ ] Data survives Docker restart
- [ ] No secrets in git
