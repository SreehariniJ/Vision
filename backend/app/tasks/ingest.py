import asyncio
import logging
import httpx
import uuid
from io import BytesIO
from sqlalchemy.orm import Session
from qdrant_client.http import models as rest

from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document, Chunk
from app.services.minio_service import minio_service
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
from app.services.graph_store import graph_store
from app.utils.chunking import chunk_text
from app.config import settings

logger = logging.getLogger(__name__)

async def extract_entities_from_chunk(chunk_text: str) -> tuple:
    """Uses local vLLM to extract entities and relationships for the Knowledge Graph."""
    prompt = f"""
You are an expert Knowledge Graph extractor. Extract entities and their relationships from the text below.
Respond ONLY with a valid JSON object in this exact format:
{{"entities": [{{"name": "...", "type": "Person/Organization/Concept"}}], "relationships": [{{"source": "...", "target": "...", "type": "..."}}]}}
Text:
{chunk_text}
"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{settings.VLLM_BASE_URL}/chat/completions",
                json={
                    "model": "Qwen/Qwen2.5-VL-7B-Instruct", # Or the default local model
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.0,
                    "max_tokens": 1024
                }
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            # Clean JSON if wrapped in markdown block
            content = content.replace("```json", "").replace("```", "").strip()
            import json
            data = json.loads(content)
            return data.get("entities", []), data.get("relationships", [])
    except Exception as e:
        logger.error(f"Entity extraction failed: {e}")
        return [], []


async def process_document_async(document_id: str):
    """Asynchronous core logic for document processing."""
    db: Session = SessionLocal()
    try:
        # 1. Fetch Document from DB
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            logger.error(f"Document {document_id} not found in DB.")
            return

        # Update status
        doc.status = 'processing'
        db.commit()

        # 2. Get file from MinIO
        file_bytes = minio_service.get_file(doc.storage_path)
        
        # 3. Parse Document (Docling or PaddleOCR)
        extracted_text = ""
        is_image = doc.mime_type and doc.mime_type.startswith('image/')
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            if is_image:
                # Use PaddleOCR
                files = {'file': (doc.filename, file_bytes, doc.mime_type)}
                response = await client.post(f"{settings.OCR_URL}/ocr", files=files)
                response.raise_for_status()
                data = response.json()
                extracted_text = data.get("full_text", "")
            else:
                # Use Docling
                files = {'file': (doc.filename, file_bytes, doc.mime_type or "application/pdf")}
                response = await client.post(f"{settings.DOCLING_URL}/parse", files=files)
                response.raise_for_status()
                data = response.json()
                extracted_text = data.get("markdown", "")
                
        if not extracted_text.strip():
            raise ValueError("No text extracted from document.")

        # 4. Chunk text
        chunks = chunk_text(extracted_text)
        logger.info(f"Document {document_id} split into {len(chunks)} chunks.")

        # 5. Get Embeddings
        embeddings = await embedding_service.get_embeddings(chunks)
        
        if len(chunks) != len(embeddings):
            raise ValueError("Mismatch between chunk count and embedding count.")

        # 6. Store in Qdrant and MySQL
        await vector_store.ensure_collection()
        
        points = []
        db_chunks = []
        
        for i, (text, emb) in enumerate(zip(chunks, embeddings)):
            chunk_id = str(uuid.uuid4())
            
            # Prepare Qdrant Point
            points.append(
                rest.PointStruct(
                    id=chunk_id,
                    vector=emb,
                    payload={
                        "document_id": document_id,
                        "chunk_index": i,
                        "text": text,
                        "filename": doc.filename
                    }
                )
            )
            
            # Prepare MySQL Record
            db_chunks.append(
                Chunk(
                    id=chunk_id,
                    document_id=document_id,
                    chunk_index=i,
                    text_content=text,
                    qdrant_id=chunk_id
                )
            )
            
            # Extract and Insert Graph Data (Background parsing)
            entities, relationships = await extract_entities_from_chunk(text)
            if entities or relationships:
                await graph_store.insert_document_graph(document_id, chunk_id, text, entities, relationships)

        # Upload to Qdrant
        await vector_store.client.upsert(
            collection_name=vector_store.collection_name,
            points=points
        )
        
        # Save to MySQL
        db.add_all(db_chunks)
        
        # Update status
        doc.status = 'indexed'
        db.commit()
        logger.info(f"Document {document_id} successfully processed and indexed.")

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}", exc_info=True)
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = 'failed'
            doc.error_message = str(e)
            db.commit()
    finally:
        db.close()


@celery_app.task(name="app.tasks.ingest.process_document")
def process_document(document_id: str):
    """
    Celery task entry point.
    Wraps the async processing logic in a synchronous execution loop.
    """
    logger.info(f"Starting Celery task for document {document_id}")
    asyncio.run(process_document_async(document_id))
