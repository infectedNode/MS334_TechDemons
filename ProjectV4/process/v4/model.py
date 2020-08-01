import tensorflow as tf

from process.v4.anchors import compute_normalized_anchors
from process.v4.backbones.csp_darknet53 import csp_darknet53
from process.v4.heads.yolov3_head import yolov3_head
from process.v4.necks.yolov4_neck import yolov4_neck
from process.v4.tools.weights import get_weights_by_keyword_or_path
def YOLOv4(
    input_shape,
    num_classes,
    anchors,
    training=False,
    yolo_max_boxes=50,
    yolo_iou_threshold=0.5,
    yolo_score_threshold=0.5,
    weights="darknet",
):
    if (input_shape[0] % 32 != 0) | (input_shape[1] % 32 != 0):
        raise ValueError(
            f"Provided height and width in input_shape {input_shape} is not a multiple of 32"
        )

    backbone = csp_darknet53(input_shape)

    neck = yolov4_neck(input_shapes=backbone.output_shape)

    normalized_anchors = compute_normalized_anchors(anchors, input_shape)
    head = yolov3_head(
        input_shapes=neck.output_shape,
        anchors=normalized_anchors,
        num_classes=num_classes,
        training=training,
        yolo_max_boxes=yolo_max_boxes,
        yolo_iou_threshold=yolo_iou_threshold,
        yolo_score_threshold=yolo_score_threshold,
    )

    inputs = tf.keras.Input(shape=input_shape)
    lower_features = backbone(inputs)
    medium_features = neck(lower_features)
    upper_features = head(medium_features)

    yolov4 = tf.keras.Model(inputs=inputs, outputs=upper_features, name="YOLOv4")

    weights_path = get_weights_by_keyword_or_path(weights, model=yolov4)
    if weights_path is not None:
        yolov4.load_weights(weights_path, by_name=True, skip_mismatch=True)

    return yolov4
