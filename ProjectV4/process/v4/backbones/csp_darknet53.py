import tensorflow as tf

from process.v4.layers import conv_bn


def residual_block(inputs, num_blocks):
    _, _, _, filters = inputs.shape
    x = inputs
    for _ in range(num_blocks):
        block_inputs = x
        x = conv_bn(x, filters, kernel_size=1, strides=1, activation="mish")
        x = conv_bn(x, filters, kernel_size=3, strides=1, activation="mish")

        x = x + block_inputs

    return x


def csp_block(inputs, filters, num_blocks):
    half_filters = filters // 2

    x = conv_bn(
        inputs,
        filters=filters,
        kernel_size=3,
        strides=2,
        zero_pad=True,
        padding="valid",
        activation="mish",
    )
    route = conv_bn(
        x, filters=half_filters, kernel_size=1, strides=1, activation="mish"
    )
    x = conv_bn(x, filters=half_filters, kernel_size=1, strides=1, activation="mish")

    x = residual_block(x, num_blocks=num_blocks)
    x = conv_bn(x, filters=half_filters, kernel_size=1, strides=1, activation="mish")
    x = tf.keras.layers.Concatenate()([x, route])

    x = conv_bn(x, filters=filters, kernel_size=1, strides=1, activation="mish")

    return x


def csp_darknet53(input_shape):
    inputs = tf.keras.Input(shape=input_shape)
    x = conv_bn(inputs, filters=32, kernel_size=3, strides=1, activation="mish")
    x = conv_bn(
        x,
        filters=64,
        kernel_size=3,
        strides=2,
        zero_pad=True,
        padding="valid",
        activation="mish",
    )
    route = conv_bn(x, filters=64, kernel_size=1, strides=1, activation="mish")

    shortcut = conv_bn(x, filters=64, kernel_size=1, strides=1, activation="mish")
    x = conv_bn(shortcut, filters=32, kernel_size=1, strides=1, activation="mish")
    x = conv_bn(x, filters=64, kernel_size=3, strides=1, activation="mish")

    x = x + shortcut
    x = conv_bn(x, filters=64, kernel_size=1, strides=1, activation="mish")
    x = tf.keras.layers.Concatenate()([x, route])
    x = conv_bn(x, filters=64, kernel_size=1, strides=1, activation="mish")
    x = csp_block(x, filters=128, num_blocks=2)
    output_1 = csp_block(x, filters=256, num_blocks=8)
    output_2 = csp_block(output_1, filters=512, num_blocks=8)
    output_3 = csp_block(output_2, filters=1024, num_blocks=4)

    return tf.keras.Model(inputs, [output_1, output_2, output_3], name="CSPDarknet53")
