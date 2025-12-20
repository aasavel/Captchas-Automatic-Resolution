import os
os.environ["KERAS_BACKEND"] = "tensorflow"

import json
import numpy as np
import tensorflow as tf
from pathlib import Path
from keras import layers
import keras

from ocr.model import build_model
from ocr.preprocess import encode_single_sample

# ================= CONFIG =================
data_dir = Path("./data/captcha_images_v2/")
batch_size = 16
img_width = 200
img_height = 50
train_size = 0.9
# =========================================


# ================= DATA ===================
images = sorted(list(map(str, data_dir.glob("*.png"))))
labels = [Path(img).stem for img in images]

characters = sorted(set(char for label in labels for char in label))

char_to_num = layers.StringLookup(
    vocabulary=characters,
    mask_token=None,
)

num_to_char = layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(),
    mask_token=None,
    invert=True,
)
# =========================================


def split_data(images, labels):
    size = len(images)
    indices = np.random.permutation(size)
    train_samples = int(size * train_size)

    return (
        images[indices[:train_samples]],
        images[indices[train_samples:]],
        labels[indices[:train_samples]],
        labels[indices[train_samples:]],
    )


x_train, x_val, y_train, y_val = split_data(
    np.array(images),
    np.array(labels),
)

train_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train))
train_ds = (
    train_ds
    .map(
        lambda x, y: encode_single_sample(
            x, y, char_to_num, img_height, img_width
        ),
        num_parallel_calls=tf.data.AUTOTUNE,
    )
    .batch(batch_size)
    .prefetch(tf.data.AUTOTUNE)
)

val_ds = tf.data.Dataset.from_tensor_slices((x_val, y_val))
val_ds = (
    val_ds
    .map(
        lambda x, y: encode_single_sample(
            x, y, char_to_num, img_height, img_width
        ),
        num_parallel_calls=tf.data.AUTOTUNE,
    )
    .batch(batch_size)
    .prefetch(tf.data.AUTOTUNE)
)

# ================= MODEL ==================
model = build_model(img_width, img_height, char_to_num)
model.summary()

model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=20,
)
# =========================================


# =========================================================
# PARTIE QUE TU N’AVAIS PAS (ET QUI MANQUAIT)
# =========================================================

Path("model").mkdir(parents=True, exist_ok=True)
#  Sauvegarder le modèle d'entraînement (avec CTC)
model.save("model/ocr_train.keras")

#  Créer le modèle d'inférence (SANS CTC)
#    → couche juste avant CTCLayer = softmax
prediction_layer = model.get_layer(index=-2)

model_infer = keras.models.Model(
    inputs=model.input[0],   # image uniquement
    outputs=prediction_layer.output,
    name="ocr_infer_model",
)

#  Sauvegarder le modèle d'inférence
model_infer.save("model/ocr_infer.keras")

#  Sauvegarder les caractères (TRÈS IMPORTANT)
with open("model/characters.json", "w") as f:
    json.dump(characters, f)

print(" Entraînement terminé")
print(" Modèles sauvegardés :")
print("   - model/ocr_train.keras")
print("   - model/ocr_infer.keras")
print("   - model/characters.json")
