from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.db.database import get_db
from app.models.models import User


def get_current_user(
    username: str = Depends(verify_token),
    db: Session  = Depends(get_db),
) -> User:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
