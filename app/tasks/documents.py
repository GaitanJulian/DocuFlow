from pathlib import Path

from celery import shared_task
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.document import Document, DocumentStatus
from app.core.celery_app import celery_app


@shared_task(name="documents.index_document")
def index_document_task(document_id: int) -> str:
    """
    Celery task that simulates indexing a document by reading it from disk,
    generating a fake 'indexed_text', and updating the document status.
    """
    db: Session = SessionLocal()
    try:
        doc: Document | None = db.query(Document).filter(Document.id == document_id).first()
        if doc is None:
            return f"Document {document_id} not found"

        # Update status to PROCESSING
        doc.status = DocumentStatus.PROCESSING
        db.commit()
        db.refresh(doc)

        # File path
        file_path = Path(settings.FILES_DIR) / doc.filename

        if not file_path.exists():
            doc.status = DocumentStatus.FAILED
            doc.indexed_text = "File not found on disk."
            db.commit()
            return f"File for document {document_id} not found"

        # Read the content (binary text; still just a simulation)
        data = file_path.read_bytes()

        # Simulate some form of "indexing"
        size_kb = len(data) / 1024
        doc.indexed_text = f"Indexed document #{doc.id}, size ~{size_kb:.2f} KB."
        doc.status = DocumentStatus.INDEXED
        db.commit()

        return f"Document {document_id} indexed successfully"

    except Exception as e:
        # On error, mark the document as FAILED
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc is not None:
            doc.status = DocumentStatus.FAILED
            doc.indexed_text = f"Indexing failed: {e}"
            db.commit()
        return f"Error indexing document {document_id}: {e}"

    finally:
        db.close()

@celery_app.task(name="app.tasks.documents.retry_failed_documents")
def retry_failed_documents_task() -> int:
    """
    Find documents marked as FAILED, queue them again for re-indexing,
    and return how many retries were triggered.
    """
    db: Session = SessionLocal()
    retried = 0
    try:
        failed_docs = (
            db.query(Document)
            .filter(Document.status == DocumentStatus.FAILED)
            .all()
        )

        for doc in failed_docs:
            # Reset status to UPLOADED/PROCESSING
            doc.status = DocumentStatus.UPLOADED
            db.commit()
            db.refresh(doc)

            # Requeue the indexing task
            index_document_task.delay(doc.id)
            retried += 1

    finally:
        db.close()

    return retried
