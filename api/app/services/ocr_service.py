import json
import tensorflow as tf
from pathlib import Path
from keras import layers
import keras

from ocr.preprocess import encode_single_sample
from ocr.decode import decode_batch_predictions

# ================= CONFIG =================
MODEL_PATH = Path("model/ocr_infer.keras")
CHAR_PATH = Path("model/characters.json")

IMG_HEIGHT = 50
IMG_WIDTH = 200
# =========================================

# ===== LOAD MODEL ONCE (au démarrage) =====
model = keras.models.load_model(MODEL_PATH, compile=False)

with open(CHAR_PATH, "r") as f:
    characters = json.load(f)

char_to_num = layers.StringLookup(vocabulary=characters, mask_token=None)

num_to_char = layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(),
    mask_token=None,
    invert=True,
)

print("✅ OCR model loaded")


def solve_captcha(image_path: str):
    """
    Inférence OCR sur un CAPTCHA (pas d'entraînement).
    Retourne (texte_prédit, confidence).
    """
    sample = encode_single_sample(
        img_path=image_path,
        label="",
        char_to_num=char_to_num,
        img_height=IMG_HEIGHT,
        img_width=IMG_WIDTH,
    )

    image = tf.expand_dims(sample["image"], axis=0)
    preds = model.predict(image, verbose=0)

    pred_text = decode_batch_predictions(preds, num_to_char)[0]

    # Confidence simple (moyenne des probas max)
    probs = tf.reduce_max(preds, axis=-1)
    confidence = float(tf.reduce_mean(probs).numpy())

    return pred_text, confidence
