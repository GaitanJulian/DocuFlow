import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

os.environ.setdefault("PGCLIENTENCODING", "LATIN1")
engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    connect_args={"client_encoding": "LATIN1"},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
