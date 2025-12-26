from scraper.scrape_captcha import scrape_captcha
from ocr.predictor import OCRPredictor

ocr = OCRPredictor("models/ocr_ctc_finetuned.keras")

def solve_captcha_from_url(url: str) -> dict:
    image_path = scrape_captcha(url)
    text = ocr.predict(image_path)

    return {
        "text": text,
        "image_path": image_path
    }
