from pathlib import Path

import numpy as np

from tf2_yolov4.tools.download import download_file_from_google_drive


TF2_YOLOV4_DEFAULT_PATH = Path.home() / ".tf2-yolov4"
DARKNET_WEIGHTS_PATH = TF2_YOLOV4_DEFAULT_PATH / "yolov4.h5"
DARKNET_ORIGINAL_WEIGHTS_PATH = TF2_YOLOV4_DEFAULT_PATH / "yolov4.weights"

YOLOV4_DARKNET_FILE_ID = "1cewMfusmPjYWbrnuJRuKhPMwRe_b9PaT"
YOLOV4_DARKNET_FILE_SIZE = 249 * 1024 * 1024

AVAILABLE_PRETRAINED_WEIGHTS_OPTIONS = ["darknet"]


def load_darknet_weights_in_yolo(yolo_model, darknet_weights_path):
    sample_conv_weights = (
        yolo_model.get_layer("CSPDarknet53").get_layer("conv2d_32").get_weights()[0]
    )

    model_layers = (
        yolo_model.get_layer("CSPDarknet53").layers
        + yolo_model.get_layer("YOLOv4_neck").layers
        + yolo_model.get_layer("YOLOv3_head").layers
    )
    conv_layers = [layer for layer in model_layers if "conv2d" in layer.name]
    batch_norm_layers = [
        layer for layer in model_layers if "batch_normalization" in layer.name
    ]
    conv_layers = [conv_layers[0]] + sorted(
        conv_layers[1:], key=lambda x: int(x.name[7:])
    )
    batch_norm_layers = [batch_norm_layers[0]] + sorted(
        batch_norm_layers[1:], key=lambda x: int(x.name[20:])
    )
    darknet_weight_file = open(darknet_weights_path, "rb")
    _ = np.fromfile(darknet_weight_file, dtype=np.int32, count=5)
    current_matching_batch_norm_index = 0

    for layer in conv_layers:
        kernel_size = layer.kernel_size
        input_filters = layer.input_shape[-1]
        filters = layer.filters
        use_bias = layer.bias is not None

        if use_bias:
            conv_bias = np.fromfile(
                darknet_weight_file, dtype=np.float32, count=filters
            )
        else:
            batch_norm_weights = np.fromfile(
                darknet_weight_file, dtype=np.float32, count=4 * filters
            ).reshape((4, filters))[[1, 0, 2, 3]]

        conv_size = kernel_size[0] * kernel_size[1] * input_filters * filters
        conv_weights = (
            np.fromfile(darknet_weight_file, dtype=np.float32, count=conv_size)
            .reshape((filters, input_filters, kernel_size[0], kernel_size[1]))
            .transpose([2, 3, 1, 0])
        )

        if use_bias:
            layer.set_weights([conv_weights, conv_bias])
        else:
            layer.set_weights([conv_weights])
            batch_norm_layers[current_matching_batch_norm_index].set_weights(
                batch_norm_weights
            )
            current_matching_batch_norm_index += 1
    remaining_chars = len(darknet_weight_file.read())
    darknet_weight_file.close()
    assert remaining_chars == 0
    sample_conv_weights_after_loading = (
        yolo_model.get_layer("CSPDarknet53").get_layer("conv2d_32").get_weights()[0]
    )
    np.testing.assert_raises(
        AssertionError,
        np.testing.assert_array_equal,
        sample_conv_weights,
        sample_conv_weights_after_loading,
    )

    return yolo_model


def get_weights_by_keyword_or_path(weights, model):
    if (
        weights not in [None, *AVAILABLE_PRETRAINED_WEIGHTS_OPTIONS]
        and not Path(weights).is_file()
    ):
        raise ValueError(
            f"`weights` argument should either be in {AVAILABLE_PRETRAINED_WEIGHTS_OPTIONS}, "
            "a path to a valid .h5 file or None (random initialization)"
        )

    if weights is None:
        return None

    if Path(weights).is_file():
        return weights

    return get_weights_by_keyword(weights, model)


def get_weights_by_keyword(weights, model):
    if weights == "darknet":
        return get_darknet_weights_path_by_download(model)

    return None


def get_darknet_weights_path_by_download(model):
    if DARKNET_WEIGHTS_PATH.is_file():
        return DARKNET_WEIGHTS_PATH

    darknet_weights_path = download_darknet_weights(model)

    return darknet_weights_path


def download_darknet_weights(yolov4_model):
    if not TF2_YOLOV4_DEFAULT_PATH.is_dir():
        TF2_YOLOV4_DEFAULT_PATH.mkdir()

    is_darknet_original_weights_available = DARKNET_ORIGINAL_WEIGHTS_PATH.is_file()

    if not is_darknet_original_weights_available:
        print("Download original Darknet weights")
        download_file_from_google_drive(
            YOLOV4_DARKNET_FILE_ID,
            DARKNET_ORIGINAL_WEIGHTS_PATH,
            target_size=YOLOV4_DARKNET_FILE_SIZE,
        )

    print("Converting original Darknet weights to .h5 format")
    yolov4 = load_darknet_weights_in_yolo(
        yolov4_model, str(DARKNET_ORIGINAL_WEIGHTS_PATH)
    )
    yolov4.save_weights(str(DARKNET_WEIGHTS_PATH))

    return DARKNET_WEIGHTS_PATH
