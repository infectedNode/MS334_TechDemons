import tensorflow as tf
from process.v4.model import YOLOv4
from process.v4.anchors import YOLOV4_ANCHORS
classes_path = './process/data/labels/coco.names'
classes_path2 = './process/data/labels/cocoorig.names'
weights_path = './process/weights/yolov4_custom.h5'
weights_path2 = './process/weights/yolov4.h5'

physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)


# Initializing YoloV4
yolo = YOLOv4(
    input_shape=(416, 416, 3),
    anchors=YOLOV4_ANCHORS,
    num_classes=1,
    training=False,
    yolo_max_boxes=100,
    yolo_iou_threshold=0.5,
    yolo_score_threshold=0.5,
)
yolo.load_weights(weights_path)
yolo2 = YOLOv4(
    input_shape=(416, 416, 3),
    anchors=YOLOV4_ANCHORS,
    num_classes=80,
    training=False,
    yolo_max_boxes=100,
    yolo_iou_threshold=0.5,
    yolo_score_threshold=0.5,
)
yolo2.load_weights(weights_path2)
# Loading Classes
class_names = [c.strip() for c in open(classes_path).readlines()]
class_names2 = [c.strip() for c in open(classes_path2).readlines()]