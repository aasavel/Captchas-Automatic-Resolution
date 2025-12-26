import time
from ocr.predictor import OCRPredictor
from scraper.scrape_captcha import scrape_captcha

MODEL_PATH = "models/ocr_ctc_robust_best.keras"

print(f"[OCR] Loading model: {MODEL_PATH}")
ocr = OCRPredictor(MODEL_PATH)

def solve_captcha_from_url(url: str):
    start = time.time()

    image_path = scrape_captcha(url)
    text = ocr.predict(image_path)

    duration = round(time.time() - start, 3)

    return {
        "text": text,
        "image_path": image_path,
        "duration_sec": duration
    }

def get_model_info():
    return {
        "model_path": MODEL_PATH,
        "type": "CTC OCR",
        "framework": "TensorFlow / Keras"
    }
