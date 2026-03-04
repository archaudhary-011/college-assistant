from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import User, Conversation, ChatMessage
from app.schemas.schemas import ConversationOut, MessageOut

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("", response_model=List[ConversationOut])
def get_conversations(
    current_user: User   = Depends(get_current_user),
    db:           Session = Depends(get_db),
):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )


@router.post("", response_model=ConversationOut, status_code=201)
def create_conversation(
    current_user: User   = Depends(get_current_user),
    db:           Session = Depends(get_db),
):
    convo = Conversation(user_id=current_user.id, title="New conversation")
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return convo


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user:    User   = Depends(get_current_user),
    db:              Session = Depends(get_db),
):
    convo = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    ).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(convo)
    db.commit()
    return {"message": "Deleted"}


@router.get("/{conversation_id}/messages", response_model=List[MessageOut])
def get_messages(
    conversation_id: int,
    current_user:    User   = Depends(get_current_user),
    db:              Session = Depends(get_db),
):
    convo = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    ).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return convo.messages
