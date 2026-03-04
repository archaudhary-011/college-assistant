# #main.py
# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.responses import FileResponse
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import List, Optional
# from jose import JWTError, jwt
# from datetime import datetime, timedelta

# from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
# from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship

# from passlib.context import CryptContext

# from .rag import generate_answer

# from dotenv import load_dotenv
# import os
# import hashlib

# load_dotenv()

# # ------------------- APP -------------------
# app = FastAPI()

# # ------------------- CORS -------------------
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ------------------- DATABASE -------------------
# DATABASE_URL = "sqlite:///./chatapp.db"

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()


# # ------------------- MODELS -------------------

# class User(Base):
#     __tablename__ = "users"

#     id               = Column(Integer, primary_key=True, index=True)
#     username         = Column(String, unique=True, index=True)
#     hashed_password  = Column(String)

#     conversations    = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


# class Conversation(Base):
#     __tablename__ = "conversations"

#     id         = Column(Integer, primary_key=True, index=True)
#     user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
#     title      = Column(String, default="New conversation")
#     created_at = Column(DateTime, default=datetime.utcnow)

#     user       = relationship("User", back_populates="conversations")
#     messages   = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ChatMessage.timestamp")


# class ChatMessage(Base):
#     __tablename__ = "chat_messages"

#     id              = Column(Integer, primary_key=True, index=True)
#     conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
#     user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
#     role            = Column(String, nullable=False)       # "user" | "assistant"
#     content         = Column(Text, nullable=False)
#     timestamp       = Column(DateTime, default=datetime.utcnow)

#     conversation    = relationship("Conversation", back_populates="messages")


# Base.metadata.create_all(bind=engine)


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # ------------------- PASSWORD HASHING -------------------
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# def hash_password(password: str):
#     sha256_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
#     return pwd_context.hash(sha256_hash)


# def verify_password(plain_password: str, hashed_password: str):
#     sha256_hash = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
#     return pwd_context.verify(sha256_hash, hashed_password)


# # ------------------- JWT CONFIG -------------------
# SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")  # prefer env var
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_HOURS = 2


# def create_access_token(username: str):
#     expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
#     payload = {"sub": username, "exp": expire}
#     return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# # ------------------- PYDANTIC SCHEMAS -------------------

# class LoginRequest(BaseModel):
#     username: str
#     password: str

# class RegisterRequest(BaseModel):
#     username: str
#     password: str

# class TokenResponse(BaseModel):
#     access_token: str
#     token_type: str

# class MessageSchema(BaseModel):
#     role: str
#     content: str

# class ChatRequest(BaseModel):
#     conversation_id: Optional[int] = None   # None → create new conversation
#     message: str                             # only the new user message

# class ConversationOut(BaseModel):
#     id: int
#     title: str
#     created_at: datetime

#     class Config:
#         from_attributes = True

# class MessageOut(BaseModel):
#     id: int
#     role: str
#     content: str
#     timestamp: datetime

#     class Config:
#         from_attributes = True


# # ------------------- TOKEN VERIFICATION -------------------
# security = HTTPBearer()


# def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     if credentials.scheme.lower() != "bearer":
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme")

#     try:
#         payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
#         return username
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or invalid")


# def get_current_user(username: str = Depends(verify_token), db: Session = Depends(get_db)) -> User:
#     user = db.query(User).filter(User.username == username).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
#     return user


# # ------------------- REGISTER -------------------
# @app.post("/register")
# def register(data: RegisterRequest, db: Session = Depends(get_db)):
#     if db.query(User).filter(User.username == data.username).first():
#         raise HTTPException(status_code=409, detail="Username already exists")

#     new_user = User(username=data.username, hashed_password=hash_password(data.password))
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return {"message": "User registered successfully"}


# # ------------------- LOGIN -------------------
# @app.post("/login", response_model=TokenResponse)
# def login(data: LoginRequest, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.username == data.username).first()

#     if not user or not verify_password(data.password, user.hashed_password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

#     return {"access_token": create_access_token(user.username), "token_type": "bearer"}


# # ------------------- CONVERSATIONS -------------------

# @app.get("/conversations", response_model=List[ConversationOut])
# def get_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     """Return all conversations for the logged-in user, newest first."""
#     return (
#         db.query(Conversation)
#         .filter(Conversation.user_id == current_user.id)
#         .order_by(Conversation.created_at.desc())
#         .all()
#     )


# @app.post("/conversations", response_model=ConversationOut)
# def create_conversation(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     """Create a blank new conversation."""
#     convo = Conversation(user_id=current_user.id, title="New conversation")
#     db.add(convo)
#     db.commit()
#     db.refresh(convo)
#     return convo


# @app.delete("/conversations/{conversation_id}")
# def delete_conversation(
#     conversation_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     convo = db.query(Conversation).filter(
#         Conversation.id == conversation_id,
#         Conversation.user_id == current_user.id
#     ).first()
#     if not convo:
#         raise HTTPException(status_code=404, detail="Conversation not found")
#     db.delete(convo)
#     db.commit()
#     return {"message": "Deleted"}


# # ------------------- MESSAGES -------------------

# @app.get("/conversations/{conversation_id}/messages", response_model=List[MessageOut])
# def get_messages(
#     conversation_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Return all messages in a conversation (must belong to the current user)."""
#     convo = db.query(Conversation).filter(
#         Conversation.id == conversation_id,
#         Conversation.user_id == current_user.id
#     ).first()
#     if not convo:
#         raise HTTPException(status_code=404, detail="Conversation not found")
#     return convo.messages


# # ------------------- CHAT -------------------

# @app.post("/chat")
# def chat(
#     request: ChatRequest,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     # 1. Resolve or create conversation
#     if request.conversation_id:
#         convo = db.query(Conversation).filter(
#             Conversation.id == request.conversation_id,
#             Conversation.user_id == current_user.id
#         ).first()
#         if not convo:
#             raise HTTPException(status_code=404, detail="Conversation not found")
#     else:
#         convo = Conversation(user_id=current_user.id, title="New conversation")
#         db.add(convo)
#         db.commit()
#         db.refresh(convo)

#     # 2. Save the user's message
#     user_msg = ChatMessage(
#         conversation_id=convo.id,
#         user_id=current_user.id,
#         role="user",
#         content=request.message,
#     )
#     db.add(user_msg)
#     db.commit()

#     # 3. Auto-title the conversation from the first message
#     if len(convo.messages) == 1:
#         convo.title = request.message[:40] + ("…" if len(request.message) > 40 else "")
#         db.commit()

#     # 4. Build full message history to pass to RAG
#     history = [{"role": m.role, "content": m.content} for m in convo.messages]

#     # 5. Generate answer
#     answer = generate_answer(history)

#     # 6. Save assistant reply
#     bot_msg = ChatMessage(
#         conversation_id=convo.id,
#         user_id=current_user.id,
#         role="assistant",
#         content=answer,
#     )
#     db.add(bot_msg)
#     db.commit()

#     return {
#         "conversation_id": convo.id,
#         "conversation_title": convo.title,
#         "answer": answer,
#     }


# # ------------------- PDF DOWNLOADS -------------------

# import math

# PDF_FOLDER = os.path.join(os.path.dirname(__file__), "pdfs")

# # Friendly display names for known files (optional — fallback is filename)
# PDF_DISPLAY_NAMES = {
#     "academic_handbook.pdf":    "Academic Handbook 2024-25",
#     "syllabus_se_comp.pdf":     "Syllabus – SE Computer Eng.",
#     "syllabus_te_comp.pdf":     "Syllabus – TE Computer Eng.",
#     "syllabus_be_comp.pdf":     "Syllabus – BE Computer Eng.",
#     "fee_structure.pdf":        "Fee Structure 2024-25",
#     "exam_schedule.pdf":        "Exam Schedule 2024-25",
#     "admission_form.pdf":       "Admission Form",
#     "scholarship_form.pdf":     "Scholarship Application Form",
#     "hostel_form.pdf":          "Hostel Admission Form",
#     "college_brochure.pdf":     "College Brochure",
# }

# def format_size(size_bytes: int) -> str:
#     if size_bytes == 0:
#         return "0 B"
#     units = ["B", "KB", "MB", "GB"]
#     i = int(math.floor(math.log(size_bytes, 1024)))
#     p = math.pow(1024, i)
#     return f"{size_bytes / p:.1f} {units[i]}"


# @app.get("/pdfs")
# def list_pdfs(current_user: User = Depends(get_current_user)):
#     """List all available PDF files for download."""
#     if not os.path.exists(PDF_FOLDER):
#         os.makedirs(PDF_FOLDER)
#         return []

#     pdf_files = sorted([f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")])

#     result = []
#     for filename in pdf_files:
#         path = os.path.join(PDF_FOLDER, filename)
#         size_bytes = os.path.getsize(path)
#         result.append({
#             "filename": filename,
#             "name": PDF_DISPLAY_NAMES.get(filename, filename.replace("_", " ").replace(".pdf", "").title()),
#             "size": format_size(size_bytes),
#         })

#     return result


# @app.get("/pdfs/download/{filename}")
# def download_pdf(
#     filename: str,
#     current_user: User = Depends(get_current_user)
# ):
#     """Download a specific PDF file."""
#     # Security: prevent path traversal
#     safe_filename = os.path.basename(filename)
#     path = os.path.join(PDF_FOLDER, safe_filename)

#     if not os.path.exists(path):
#         raise HTTPException(status_code=404, detail="File not found")

#     if not safe_filename.endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Only PDF files are allowed")

#     return FileResponse(
#         path=path,
#         media_type="application/pdf",
#         filename=safe_filename,
#         headers={"Content-Disposition": f"attachment; filename={safe_filename}"}
#     )



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