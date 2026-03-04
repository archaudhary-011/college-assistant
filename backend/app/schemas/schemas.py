from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ── Auth ──────────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str


# ── Chat ──────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None  # None → create new conversation
    message:         str


# ── Conversation ──────────────────────────────────────────────────────────────
class ConversationOut(BaseModel):
    id:         int
    title:      str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Message ───────────────────────────────────────────────────────────────────
class MessageOut(BaseModel):
    id:        int
    role:      str
    content:   str
    timestamp: datetime

    class Config:
        from_attributes = True
