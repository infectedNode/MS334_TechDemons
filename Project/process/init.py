import tensorflow as tf
from process.yolov3_tf2.models import YoloV3

classes_path = './process/data/labels/coco.names'
weights_path = './process/weights/yolov3.tf'
num_classes = 80

physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)


# Initializing YoloV3
yolo = YoloV3(classes=num_classes)

# Loading Weights
yolo.load_weights(weights_path).expect_partial()

# Loading Classes
class_names = [c.strip() for c in open(classes_path).readlines()]