import tensorflow as tf

from process.v4.layers import conv_bn
def yolov4_neck(input_shapes):
    input_1 = tf.keras.Input(shape=filter(None, input_shapes[0]))
    input_2 = tf.keras.Input(shape=filter(None, input_shapes[1]))
    input_3 = tf.keras.Input(shape=filter(None, input_shapes[2]))

    x = conv_bn(input_3, filters=512, kernel_size=1, strides=1, activation="leaky_relu")
    x = conv_bn(x, filters=1024, kernel_size=3, strides=1, activation="leaky_relu")
    x = conv_bn(x, filters=512, kernel_size=1, strides=1, activation="leaky_relu")

    maxpool_1 = tf.keras.layers.MaxPool2D((5, 5), strides=1, padding="same")(x)
    maxpool_2 = tf.keras.layers.MaxPool2D((9, 9), strides=1, padding="same")(x)
    maxpool_3 = tf.keras.layers.MaxPool2D((13, 13), strides=1, padding="same")(x)

    spp = tf.keras.layers.Concatenate()([maxpool_3, maxpool_2, maxpool_1, x])

    x = conv_bn(spp, filters=512, kernel_size=1, strides=1, activation="leaky_relu")
    x = conv_bn(x, filters=1024, kernel_size=3, strides=1, activation="leaky_relu")
    output_3 = conv_bn(
        x, filters=512, kernel_size=1, strides=1, activation="leaky_relu"
    )
    x = conv_bn(
        output_3, filters=256, kernel_size=1, strides=1, activation="leaky_relu"
    )

    upsampled = tf.keras.layers.UpSampling2D()(x)

    x = conv_bn(input_2, filters=256, kernel_size=1, strides=1, activation="leaky_relu")
    x = tf.keras.layers.Concatenate()([x, upsampled])

    x = conv_bn(x, filters=256, kernel_size=1, strides=1, activation="leaky_relu")
    x = conv_bn(x, filters=512, kernel_size=3, strides=1, activation="leaky_relu")
    x = conv_bn(x, filters=256, kernel_size=1, strides=1, activation="leaky_relu")
    x = conv_bn(x, filters=512, kernel_size=3, strides=1, activation="leaky_relu")
    output_2 = conv_bn(
        x, filters=256, kernel_size=1, strides=1, activation="leaky_relu"
    )
    x = conv_bn(
        output_2, filters=128, kernel_size=1, strides=1, activation="leaky_relu"
    )

    upsampled = tf.keras.layers.UpSampling2D()(x)

    x = conv_bn(input_1, filters=128, kernel_size=1, strides=1, activation="leaky_relu")
    x = tf.keras.layers.Concatenate()([x, upsampled])

    x = conv_bn(x, filters=128, kernel_size=1, strides=1, activation="leaky_relu")
    x = conv_bn(x, filters=256, kernel_size=3, strides=1, activation="leaky_relu")
    x = conv_bn(x, filters=128, kernel_size=1, strides=1, activation="leaky_relu")
    x = conv_bn(x, filters=256, kernel_size=3, strides=1, activation="leaky_relu")
    output_1 = conv_bn(
        x, filters=128, kernel_size=1, strides=1, activation="leaky_relu"
    )

    return tf.keras.Model(
        [input_1, input_2, input_3], [output_1, output_2, output_3], name="YOLOv4_neck"
    )
