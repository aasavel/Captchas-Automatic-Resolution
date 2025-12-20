import tensorflow as tf
from keras import ops


def decode_batch_predictions(pred, num_to_char):
    input_len = ops.ones(pred.shape[0]) * pred.shape[1]

    results = tf.keras.backend.ctc_decode(
        pred,
        input_length=input_len,
        greedy=True,
    )[0][0]

    output_text = []
    for res in results:
        chars = num_to_char(res)


        chars = tf.boolean_mask(
            chars,
            tf.not_equal(chars, "[UNK]")
        )

        text = tf.strings.reduce_join(chars).numpy().decode("utf-8")
        output_text.append(text)

    return output_text
