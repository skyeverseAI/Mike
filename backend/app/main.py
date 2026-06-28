from fastapi import FastAPI
from app.api.routes import auth
from app.models import user, workspace 

app = FastAPI(title="Mike Legal AI")

app.include_router(auth.router)

@app.get("/health")
def health():
    return {"status": "ok"}