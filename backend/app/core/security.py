import hashlib
from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_HOURS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security    = HTTPBearer()


# ── Password ──────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    sha256 = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(sha256)


def verify_password(plain: str, hashed: str) -> bool:
    sha256 = hashlib.sha256(plain.encode("utf-8")).hexdigest()
    return pwd_context.verify(sha256, hashed)


# ── JWT ───────────────────────────────────────────────────────────────────────
def create_access_token(username: str) -> str:
    expire  = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication scheme",
        )
    try:
        payload  = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or invalid")
