from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import User, Conversation, ChatMessage
from app.schemas.schemas import ChatRequest
from app.services.rag import generate_answer

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("")
def chat(
    request:      ChatRequest,
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db),
):
    # 1. Resolve or create conversation
    if request.conversation_id:
        convo = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id,
        ).first()
        if not convo:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        convo = Conversation(user_id=current_user.id, title="New conversation")
        db.add(convo)
        db.commit()
        db.refresh(convo)

    # 2. Save user message
    user_msg = ChatMessage(
        conversation_id=convo.id,
        user_id=current_user.id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(convo)

    # 3. Auto-title from first message
    if len(convo.messages) == 1:
        convo.title = request.message[:40] + ("…" if len(request.message) > 40 else "")
        db.commit()

    # 4. Build history and generate answer
    history = [{"role": m.role, "content": m.content} for m in convo.messages]
    answer  = generate_answer(history)

    # 5. Save assistant reply
    bot_msg = ChatMessage(
        conversation_id=convo.id,
        user_id=current_user.id,
        role="assistant",
        content=answer,
    )
    db.add(bot_msg)
    db.commit()

    return {
        "conversation_id":    convo.id,
        "conversation_title": convo.title,
        "answer":             answer,
    }
