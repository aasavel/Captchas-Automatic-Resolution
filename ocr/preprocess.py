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
