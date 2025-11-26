from fastapi import APIRouter

from app.api.routes_auth import router as auth_router
from app.api.routes_documents import router as documents_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(documents_router)
