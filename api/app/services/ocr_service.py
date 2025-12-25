from ocr.predictor import OCRPredictor

# Chargement du modèle UNE SEULE FOIS (au démarrage de l'API)
ocr_model = OCRPredictor(
    model_path="models/ocr_ctc_finetuned.keras"
)

def solve_captcha(image_path: str):
    """
    Résout un CAPTCHA via le modèle OCR réel.
    """
    text = ocr_model.predict(image_path)

    # Confidence proxy (le modèle ne la fournit pas encore)
    confidence = 0.9

    return text, confidence
