import os
os.environ["KERAS_BACKEND"] = "tensorflow"

import json
import tensorflow as tf
from pathlib import Path
from keras import layers
import keras

from ocr.preprocess import encode_single_sample
from ocr.decode import decode_batch_predictions

# ================= CONFIG =================
DATA_DIR = Path("./data/captcha_images_v2/")
MODEL_PATH = "model/ocr_infer.keras"
CHAR_PATH = "model/characters.json"

IMG_HEIGHT = 50
IMG_WIDTH = 200

NB_IMAGES_TEST = 10   # nombre d'images à tester
# =========================================


# ================= LOAD MODEL =================
model = keras.models.load_model(
    MODEL_PATH,
    compile=False,
)
print("✅ Modèle OCR chargé")


# ================= LOAD CHARACTERS =================
with open(CHAR_PATH, "r") as f:
    characters = json.load(f)

char_to_num = layers.StringLookup(
    vocabulary=characters,
    mask_token=None,
)

num_to_char = layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(),
    mask_token=None,
    invert=True,
)

print("✅ Mapping caractères chargé")


# ================= TEST OCR =================
images = sorted(list(DATA_DIR.glob("*.png")))

print("\n🔎 TEST OCR SUR QUELQUES IMAGES\n")

for img_path in images[:NB_IMAGES_TEST]:
    # Le vrai texte = nom du fichier
    true_text = img_path.stem

    sample = encode_single_sample(
        img_path=str(img_path),
        label="",
        char_to_num=char_to_num,
        img_height=IMG_HEIGHT,
        img_width=IMG_WIDTH,
    )

    image = tf.expand_dims(sample["image"], axis=0)

    preds = model.predict(image, verbose=0)

    pred_text = decode_batch_predictions(
        preds,
        num_to_char,
    )[0]

    print(f" {img_path.name}")
    print(f"    Vrai      : {true_text}")
    print(f"    Prédit    : {pred_text}")
    print("-" * 40)

print("\n Test terminé")
