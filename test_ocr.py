from ocr.predictor import OCRPredictor

ocr = OCRPredictor(
    model_path="models/ocr_ctc_finetuned.keras"
)

image_path = "./data/all_captcha_png_shuffled/ScipD.png"  

text = ocr.predict(image_path)

print("Prediction OCR :", text)
