from datetime import datetime, timedelta
from typing import Optional, Any, Dict

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings


# ============================
# CONFIG JWT / SECRET KEY
# ============================

# Soporta ambos nombres de config:
# - JWT_SECRET_KEY / JWT_ALGORITHM
# - SECRET_KEY / ALGORITHM
SECRET_KEY: str = getattr(settings, "JWT_SECRET_KEY", None) or getattr(
    settings, "SECRET_KEY", "change_me"
)
ALGORITHM: str = getattr(settings, "JWT_ALGORITHM", None) or getattr(
    settings, "ALGORITHM", "HS256"
)
ACCESS_TOKEN_EXPIRE_MINUTES: int = getattr(
    settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60
)


# ============================
# PASSWORD HASHING
# ============================

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# ============================
# OAUTH2 / JWT
# ============================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Return the decoded payload or None if the token is invalid.
    (Change this to raise an exception if your code prefers that behavior.)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
