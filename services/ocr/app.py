import io
import logging
import os
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from paddleocr import PaddleOCR
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ocr-service")

app = FastAPI(title="PaddleOCR Service")

LANG = os.environ.get("OCR_LANG", "en")
DET_MODEL_DIR = os.environ.get("PADDLEOCR_DET_MODEL_DIR")
REC_MODEL_DIR = os.environ.get("PADDLEOCR_REC_MODEL_DIR")
CLS_MODEL_DIR = os.environ.get("PADDLEOCR_CLS_MODEL_DIR")


def _validate_optional_dir(label: str, value: str | None) -> None:
    if value and not Path(value).exists():
        raise RuntimeError(f"{label} was set but does not exist: {value}")


def _load_ocr() -> PaddleOCR:
    _validate_optional_dir("PADDLEOCR_DET_MODEL_DIR", DET_MODEL_DIR)
    _validate_optional_dir("PADDLEOCR_REC_MODEL_DIR", REC_MODEL_DIR)
    _validate_optional_dir("PADDLEOCR_CLS_MODEL_DIR", CLS_MODEL_DIR)

    kwargs = {
        "use_angle_cls": True,
        "lang": LANG,
        "show_log": False,
    }
    if DET_MODEL_DIR:
        kwargs["det_model_dir"] = DET_MODEL_DIR
    if REC_MODEL_DIR:
        kwargs["rec_model_dir"] = REC_MODEL_DIR
    if CLS_MODEL_DIR:
        kwargs["cls_model_dir"] = CLS_MODEL_DIR

    logger.info("Loading PaddleOCR: lang=%s", LANG)
    try:
        loaded_ocr = PaddleOCR(**kwargs)
    except Exception as exc:
        logger.exception("PaddleOCR initialization failed")
        raise RuntimeError(f"Failed to initialize PaddleOCR: {exc}") from exc
    logger.info("PaddleOCR loaded successfully")
    return loaded_ocr


ocr = _load_ocr()


@app.get("/health")
def health_check():
    return {"status": "ok", "language": LANG}


@app.post("/ocr")
async def perform_ocr(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    try:
        content = await file.read()
        image = Image.open(io.BytesIO(content)).convert("RGB")
        img_array = np.array(image)

        result = ocr.ocr(img_array, cls=True)

        extracted_text = []
        full_text = ""

        if result and result[0]:
            for line in result[0]:
                box = line[0]
                text = line[1][0]
                confidence = line[1][1]

                extracted_text.append(
                    {
                        "text": text,
                        "confidence": float(confidence),
                        "box": box,
                    }
                )
                full_text += text + "\n"

        return {
            "filename": file.filename,
            "full_text": full_text.strip(),
            "lines": extracted_text,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
