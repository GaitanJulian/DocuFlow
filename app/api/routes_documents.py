from typing import List, Optional
from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentRead


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "/", response_model=DocumentRead, status_code=status.HTTP_201_CREATED
)
def create_document(
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    doc = Document(
        owner_id=current_user.id,
        filename=payload.filename,
        content_type=payload.content_type,
        tags=payload.tags,
        status=DocumentStatus.UPLOADED,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/", response_model=List[DocumentRead])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: Optional[DocumentStatus] = None,
    q: Optional[str] = None,
) -> list[DocumentRead]:
    query = db.query(Document).filter(Document.owner_id == current_user.id)

    if status_filter:
        query = query.filter(Document.status == status_filter)

    if q:
        # búsqueda muy simple sobre filename o tags
        like = f"%{q}%"
        query = query.filter(
            (Document.filename.ilike(like)) | (Document.tags.ilike(like))
        )

    return query.order_by(Document.created_at.desc()).all()


@router.post("/{document_id}/index", response_model=DocumentRead)
def index_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    """
    Simula el proceso de indexación:
    - Cambia status a INDEXED
    - Genera un texto 'indexado' dummy
    """
    doc = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.owner_id == current_user.id,
        )
        .first()
    )

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    doc.status = DocumentStatus.INDEXED
    doc.indexed_text = f"Indexed content for {doc.filename} (simulated)."

    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Sube un archivo real y crea un registro de Document asociado al usuario actual.
    """
    # Crear directorio si no existe
    upload_dir = Path(settings.FILES_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Nombre único para almacenar el archivo
    ext = Path(file.filename).suffix
    stored_name = f"{uuid4().hex}{ext}"
    file_path = upload_dir / stored_name

    # Leer contenido y guardar en disco
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    document = Document(
    owner_id=current_user.id,
    filename=stored_name,
    content_type=file.content_type or "application/octet-stream",
    status=DocumentStatus.UPLOADED,
    # guardamos el “title” en tags para no perderlo del todo
    tags=title,
)

    db.add(document)
    db.commit()
    db.refresh(document)

    return document