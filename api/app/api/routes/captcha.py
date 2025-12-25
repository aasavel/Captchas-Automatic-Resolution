from fastapi import APIRouter, UploadFile, File
import shutil
import tempfile
import os

from api.app.services.ocr_service import solve_captcha

router = APIRouter()

@router.post("/solve")
def solve(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        text, confidence = solve_captcha(tmp_path)
    finally:
        os.remove(tmp_path)

    return {
        "captcha_type": "text",
        "prediction": text,
        "confidence": confidence,
        "model_version": "ocr_ctc_finetuned"
    }
