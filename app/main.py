# app/main.py
from fastapi import FastAPI

from app.api import router as api_router
from app.db.base import Base
from app.db.session import engine

# IMPORTA los modelos aquí para que se registren en Base.metadata
import app.models  # noqa


app = FastAPI(title="DocuFlow")


@app.on_event("startup")
def on_startup() -> None:
    # Esto creará las tablas para todos los modelos registrados
    Base.metadata.create_all(bind=engine)


app.include_router(api_router)
