# app/main.py
from fastapi import FastAPI

from app.api import router as api_router
from app.db.base import Base
from app.db.session import engine

# IMPORT the models here so they register with Base.metadata
import app.models  # noqa


app = FastAPI(title="DocuFlow")


@app.on_event("startup")
def on_startup() -> None:
    # This will create tables for every registered model
    Base.metadata.create_all(bind=engine)


app.include_router(api_router)
