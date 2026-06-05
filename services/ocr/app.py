import os
import io
import numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException
from paddleocr import PaddleOCR

app = FastAPI(title="PaddleOCR Service")

# Initialize OCR
LANG = os.environ.get("OCR_LANG", "en")
ocr = PaddleOCR(use_angle_cls=True, lang=LANG, show_log=False)

@app.get("/health")
def health_check():
    return {"status": "ok", "language": LANG}

@app.post("/ocr")
async def perform_ocr(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    try:
        content = await file.read()
        image = Image.open(io.BytesIO(content)).convert('RGB')
        img_array = np.array(image)
        
        # Perform OCR
        result = ocr.ocr(img_array, cls=True)
        
        extracted_text = []
        full_text = ""
        
        if result and result[0]:
            for line in result[0]:
                box = line[0]
                text = line[1][0]
                confidence = line[1][1]
                
                extracted_text.append({
                    "text": text,
                    "confidence": float(confidence),
                    "box": box
                })
                full_text += text + "\n"
                
        return {
            "filename": file.filename,
            "full_text": full_text.strip(),
            "lines": extracted_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
