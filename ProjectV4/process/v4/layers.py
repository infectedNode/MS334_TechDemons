import tensorflow as tf
import tensorflow_addons as tfa
def conv_bn(
    inputs,
    filters,
    kernel_size,
    strides,
    padding="same",
    zero_pad=False,
    activation="leaky",
):
    if zero_pad:
        inputs = tf.keras.layers.ZeroPadding2D(((1, 0), (1, 0)))(inputs)

    x = tf.keras.layers.Conv2D(
        filters=filters,
        kernel_size=kernel_size,
        strides=strides,
        padding=padding,
        use_bias=False,
    )(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    if activation == "leaky_relu":
        x = tf.keras.layers.LeakyReLU(alpha=0.1)(x)
    elif activation == "mish":
        x = tfa.activations.mish(x)

    return x
