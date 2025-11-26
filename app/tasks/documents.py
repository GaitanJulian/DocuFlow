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
    Tarea de Celery que simula la indexación de un documento:
    - Lee el archivo desde disco.
    - Genera un 'indexed_text' simulado.
    - Actualiza el estado del documento.
    """
    db: Session = SessionLocal()
    try:
        doc: Document | None = db.query(Document).filter(Document.id == document_id).first()
        if doc is None:
            return f"Document {document_id} not found"

        # Actualizar estado a PROCESSING
        doc.status = DocumentStatus.PROCESSING
        db.commit()
        db.refresh(doc)

        # Ruta del archivo
        file_path = Path(settings.FILES_DIR) / doc.filename

        if not file_path.exists():
            doc.status = DocumentStatus.FAILED
            doc.indexed_text = "File not found on disk."
            db.commit()
            return f"File for document {document_id} not found"

        # Leemos el contenido (texto binario, aquí solo simulamos)
        data = file_path.read_bytes()

        # Simular algún tipo de "indexación"
        size_kb = len(data) / 1024
        doc.indexed_text = f"Indexed document #{doc.id}, size ~{size_kb:.2f} KB."
        doc.status = DocumentStatus.INDEXED
        db.commit()

        return f"Document {document_id} indexed successfully"

    except Exception as e:
        # En caso de error, marcamos como FAILED
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
    Busca documentos con estado FAILED y vuelve a encolarlos
    para reindexar.
    Devuelve cuántos documentos se reintentaron.
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
            # Volvemos a marcar como UPLOADED/PROCESSING
            doc.status = DocumentStatus.UPLOADED
            db.commit()
            db.refresh(doc)

            # Encolamos de nuevo la tarea de indexado
            index_document_task.delay(doc.id)
            retried += 1

    finally:
        db.close()

    return retried