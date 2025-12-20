from keras import layers
import keras
from .ctc import CTCLayer


def build_model(img_width, img_height, char_to_num):
    # ================= INPUTS =================
    input_img = layers.Input(
        shape=(img_width, img_height, 1),
        name="image",
        dtype="float32",
    )
    labels = layers.Input(
        name="label",
        shape=(None,),
        dtype="float32",
    )

    # ================= CNN =================
    x = layers.Conv2D(
        32, (3, 3),
        activation="relu",
        padding="same",
        kernel_initializer="he_normal",
    )(input_img)
    x = layers.MaxPooling2D((2, 2))(x)

    x = layers.Conv2D(
        64, (3, 3),
        activation="relu",
        padding="same",
        kernel_initializer="he_normal",
    )(x)
    x = layers.MaxPooling2D((2, 2))(x)

    # ================= RESHAPE =================
    new_shape = (
        img_width // 4,
        (img_height // 4) * 64,
    )
    x = layers.Reshape(target_shape=new_shape)(x)
    x = layers.Dense(64, activation="relu")(x)
    x = layers.Dropout(0.2)(x)

    # ================= RNN =================
    x = layers.Bidirectional(
        layers.LSTM(128, return_sequences=True, dropout=0.25)
    )(x)
    x = layers.Bidirectional(
        layers.LSTM(64, return_sequences=True, dropout=0.25)
    )(x)

    # ================= SOFTMAX =================
    x = layers.Dense(
        len(char_to_num.get_vocabulary()) + 1,
        activation="softmax",
        name="softmax",
    )(x)

    # ================= CTC =================
    output = CTCLayer(name="ctc_loss")(labels, x)

    model = keras.models.Model(
        inputs=[input_img, labels],
        outputs=output,
        name="ocr_train_model",
    )

    model.compile(
        optimizer=keras.optimizers.Adam()
    )

    return model
