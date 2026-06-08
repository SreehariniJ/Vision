import logging
import os
import tempfile
from pathlib import Path

from docling.document_converter import DocumentConverter
from fastapi import FastAPI, File, HTTPException, UploadFile

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("docling-service")

app = FastAPI(title="Docling Document Parser")


def _load_converter() -> DocumentConverter:
    logger.info("Initializing Docling DocumentConverter")
    try:
        loaded_converter = DocumentConverter()
    except Exception as exc:
        logger.exception("Docling converter initialization failed")
        raise RuntimeError(f"Failed to initialize Docling DocumentConverter: {exc}") from exc
    logger.info("Docling DocumentConverter ready")
    return loaded_converter


converter = _load_converter()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/parse")
async def parse_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    tmp_path: str | None = None
    try:
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = converter.convert(tmp_path)
        markdown_text = result.document.export_to_markdown()

        return {
            "filename": file.filename,
            "markdown": markdown_text,
        }
    except Exception as exc:
        logger.exception("Docling parse failed for %s", file.filename)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
