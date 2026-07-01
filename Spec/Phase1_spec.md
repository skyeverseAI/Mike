# Phase 1 — Implementation Spec

## Status
- [x] Git initialised
- [x] `.gitignore` updated
- [x] `.env` created
- [x] `.env.example` created
- [x] Docker Compose + PostgreSQL
- [x] FastAPI skeleton + /health
- [ ] SQLAlchemy models + Alembic
- [x] JWT auth
- [x] Workspace CRUD
- [x] Next.js frontend

---

## Step 1 — Docker Compose + PostgreSQL

### What to create
`docker-compose.yml` at project root.

### File
```yaml
services:
  db:
    image: postgres:16
    restart: always
    env_file: .env
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### .env must have
```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
```

### Commands
```bash
docker compose up -d db
docker compose ps        # db should show running
```

---

## Step 2 — FastAPI Skeleton

### What to create
```
backend/
├── app/
│   ├── main.py
│   └── core/
│       └── config.py
├── Dockerfile
└── requirements.txt
```

### requirements.txt
```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
alembic
python-jose[cryptography]
passlib[bcrypt]
python-dotenv
pydantic-settings
```

### app/core/config.py
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### app/main.py
```python
from fastapi import FastAPI

app = FastAPI(title="Mike Legal AI")

@app.get("/health")
def health():
    return {"status": "ok"}
```

### Dockerfile (backend)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Add to docker-compose.yml
```yaml
  backend:
    build: ./backend
    restart: always
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      - db
    volumes:
      - ./backend:/app
```

### Commands
```bash
docker compose up -d backend
curl http://localhost:8000/health
# expected: {"status":"ok"}
```

---

## Step 3 — SQLAlchemy Models + Alembic

### What to create
```
backend/
├── app/
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   └── models/
│       ├── user.py
│       └── workspace.py
├── alembic/
│   └── versions/
└── alembic.ini
```

### app/db/base.py
```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

### app/db/session.py
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### app/models/user.py
```python
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    workspaces: Mapped[list["Workspace"]] = relationship("Workspace", back_populates="owner")
```

### app/models/workspace.py
```python
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner: Mapped["User"] = relationship("User", back_populates="workspaces")
```

### Alembic setup commands
```bash
cd backend
alembic init alembic
```

### alembic/env.py — update these two lines
```python
from app.db.base import Base
from app.models import user, workspace      # import models so Alembic sees them
target_metadata = Base.metadata
```

### alembic.ini — update this line
```
sqlalchemy.url = # leave blank — set via env.py
```

### alembic/env.py — also add DATABASE_URL from env
```python
from app.core.config import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

### Commands
```bash
alembic revision --autogenerate -m "create users and workspaces"
alembic upgrade head
```

---

## Step 4 — JWT Authentication

### What to create
```
backend/app/
├── core/
│   └── security.py
├── schemas/
│   └── user.py
└── api/
    ├── deps.py
    └── routes/
        └── auth.py
```

### app/core/security.py
```python
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "exp": expire}, settings.JWT_SECRET, settings.JWT_ALGORITHM)

def decode_token(token: str) -> str:
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    return payload["sub"]
```

### app/schemas/user.py
```python
from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

### app/api/deps.py
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_token
from app.models.user import User

bearer = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        user_id = decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
```

### app/api/routes/auth.py
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=body.email, hashed_password=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id))

@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(user.id))
```

### Register router in app/main.py
```python
from app.api.routes import auth
app.include_router(auth.router)
```

### Commands
```bash
# Test register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret123"}'

# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret123"}'
```

---

## Step 5 — Workspace CRUD

### What to create
```
backend/app/
├── schemas/
│   └── workspace.py
└── api/routes/
    └── workspaces.py
```

### app/schemas/workspace.py
```python
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
```

### app/api/routes/workspaces.py
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.post("/", response_model=WorkspaceResponse)
def create_workspace(body: WorkspaceCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ws = Workspace(name=body.name, owner_id=user.id)
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws

@router.get("/", response_model=list[WorkspaceResponse])
def list_workspaces(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Workspace).filter(Workspace.owner_id == user.id).all()

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(workspace_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ws = db.query(Workspace).filter(Workspace.id == workspace_id, Workspace.owner_id == user.id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws

@router.delete("/{workspace_id}", status_code=204)
def delete_workspace(workspace_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ws = db.query(Workspace).filter(Workspace.id == workspace_id, Workspace.owner_id == user.id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    db.delete(ws)
    db.commit()
```

### Register router in app/main.py
```python
from app.api.routes import auth, workspaces
app.include_router(workspaces.router)
```

---

## Step 6 — Next.js Frontend

### Setup commands
```bash
cd mike-legal-ai
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
```

### What to create
```
frontend/app/
├── (auth)/
│   ├── login/page.tsx       # login form
│   └── register/page.tsx    # register form
├── dashboard/
│   └── page.tsx             # list workspaces, create workspace
└── layout.tsx

frontend/lib/
└── api.ts                   # fetch wrapper with JWT header
```

### lib/api.ts
```typescript
const BASE = "http://localhost:8000";

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = localStorage.getItem("token");
  return fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
}
```

### Add to docker-compose.yml
```yaml
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### frontend/Dockerfile
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]
```

---

## Final Checks

```bash
docker compose up -d
curl http://localhost:8000/health          # {"status":"ok"}
curl http://localhost:3000                 # Next.js loads
```

### Done When
- [ ] `docker compose up` starts all services
- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] User can register
- [ ] User can login
- [ ] User can create, list, delete workspaces
- [ ] Data survives `docker compose down && docker compose up`
- [ ] No secrets in git
