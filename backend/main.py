from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.api.routes import auth, conversations, chat

# ── Create tables ─────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="College Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(chat.router)
# app.include_router(pdfs.router)


@app.get("/")
def root():
    return {"message": "College Assistant API is running 🎓"}