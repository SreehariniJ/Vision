import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from docling.document_converter import DocumentConverter

app = FastAPI(title="Docling Document Parser")

converter = DocumentConverter()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/parse")
async def parse_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    try:
        # Save uploaded file temporarily
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
            
        # Parse document
        result = converter.convert(tmp_path)
        markdown_text = result.document.export_to_markdown()
        
        # Cleanup
        os.unlink(tmp_path)
        
        return {
            "filename": file.filename,
            "markdown": markdown_text
        }
    except Exception as e:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))
