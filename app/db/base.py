# app/db/base.py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# importa modelos aquí para que Alembic los vea
from app.models.user import User  # noqa
from app.models.document import Document  # noqa
