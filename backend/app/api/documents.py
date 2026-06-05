from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import uuid
import logging

from app.core.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.services.minio_service import minio_service
from app.tasks.ingest import process_document

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document for processing.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
        
    document_id = str(uuid.uuid4())
    # TODO: In production, get user_id from auth token. Using dummy for now.
    user_id = "admin_user" 
    
    try:
        # Read file
        content = await file.read()
        file_size = len(content)
        
        # Upload to MinIO
        object_name = f"{user_id}/{document_id}/{file.filename}"
        storage_path = minio_service.upload_file(object_name, content, content_type=file.content_type)
        
        # Create DB record
        new_doc = Document(
            id=document_id,
            user_id=user_id,
            filename=file.filename,
            file_size=file_size,
            mime_type=file.content_type,
            storage_path=storage_path,
            status='queued'
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        
        # Trigger Celery Task
        process_document.delay(document_id)
        
        return new_doc
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}/status", response_model=DocumentResponse)
async def get_document_status(document_id: str, db: Session = Depends(get_db)):
    """
    Get the processing status of a document.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return doc
