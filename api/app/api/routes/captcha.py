from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/solve")
def solve_captcha(file: UploadFile = File(...)):
    return {
        "captcha_type": "text",
        "prediction": "AB7K",
        "confidence": 0.92,
        "model_version": "mock-crnn-v1",
        "processing_time_ms": 123
    }

