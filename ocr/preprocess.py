import tensorflow as tf
from keras import ops


def encode_single_sample(
    img_path,
    label,
    char_to_num,
    img_height,
    img_width,
):
    img = tf.io.read_file(img_path)
    img = tf.io.decode_png(img, channels=1)
    img = tf.image.convert_image_dtype(img, tf.float32)

    img = ops.image.resize(img, [img_height, img_width])
    img = ops.transpose(img, axes=[1, 0, 2])

    label = char_to_num(
        tf.strings.unicode_split(label, input_encoding="UTF-8")
    )

    return {"image": img, "label": label}


def preprocess_image_bytes(img_bytes, img_height, img_width):
    """
    Preprocess image for inference (no label).
    Output shape: (1, img_width, img_height, 1)
    """
    img = tf.io.decode_image(
        img_bytes, channels=1, expand_animations=False
    )
    img = tf.image.convert_image_dtype(img, tf.float32)

    img = ops.image.resize(img, [img_height, img_width])
    img = ops.transpose(img, axes=[1, 0, 2])
    img = ops.expand_dims(img, axis=0)  # batch dim

    return img
