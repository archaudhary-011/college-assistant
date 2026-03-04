from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse

# router = APIRouter(prefix="/auth", tags=["Auth"])
router = APIRouter(tags=["Auth"])


@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=409, detail="Username already exists")

    user = User(username=data.username, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return {"access_token": create_access_token(user.username), "token_type": "bearer"}
