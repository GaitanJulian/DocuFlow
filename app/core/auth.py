from datetime import timedelta

from app.core.security import create_access_token, decode_access_token
from app.schemas.auth import TokenData


def build_token(subject: dict, expires_delta: timedelta | None = None) -> str:
    return create_access_token(subject, expires_delta)


def validate_token(token: str) -> TokenData:
    return decode_access_token(token)
