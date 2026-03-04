from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    conversations   = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    title      = Column(String, default="New conversation")
    created_at = Column(DateTime, default=datetime.utcnow)

    user     = relationship("User", back_populates="conversations")
    messages = relationship(
        "ChatMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ChatMessage.timestamp",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id              = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    role            = Column(String, nullable=False)   # "user" | "assistant"
    content         = Column(Text, nullable=False)
    timestamp       = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
