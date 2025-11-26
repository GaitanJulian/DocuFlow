from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_admin
from app.models.user import User
from app.models.document import Document
from app.tasks.documents import retry_failed_documents_task

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    total_users = db.query(User).count()
    total_docs = db.query(Document).count()

    indexed_docs = db.query(Document).filter(Document.status == "INDEXED").count()
    failed_docs = db.query(Document).filter(Document.status == "FAILED").count()

    return {
        "total_users": total_users,
        "total_documents": total_docs,
        "indexed_documents": indexed_docs,
        "failed_documents": failed_docs,
    }


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "is_active": u.is_active,
            "is_admin": u.is_admin,
            "created_at": u.created_at,
        }
        for u in users
    ]


@router.get("/documents")
def list_all_documents(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    docs = db.query(Document).all()
    return [
        {
            "id": d.id,
            "owner_id": d.owner_id,
            "filename": d.filename,
            "status": d.status,
            "created_at": d.created_at,
        }
        for d in docs
    ]

@router.post("/documents/retry-failed")
def retry_failed_documents_manual(
    current_admin: User = Depends(get_current_admin),
):
    """
    Trigger a retry for FAILED documents through the API.
    """
    async_result = retry_failed_documents_task.delay()
    return {
        "detail": "Retry of failed documents triggered",
        "task_id": async_result.id,
    }
