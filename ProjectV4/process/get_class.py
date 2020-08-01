import tensorflow as tf
from process.yolov3_tf2.dataset import transform_images

from process.init import yolo2, class_names2
size = 416

def getClass(image=None):
    raw_img = tf.image.decode_image(open(image, 'rb').read(), channels=3)
    img = tf.expand_dims(raw_img, 0)
    img = transform_images(img, size)

    boxes, scores, classes, nums = yolo2(img)

    class_name = None
    count = 0
  
    for i in range(nums[0]):
        temp_class = class_names[int(classes[0][i])]
        if (temp_class=="suitcase" or temp_class=="handbag" or temp_class=="backpack"):
            count += 1
            class_name = temp_class    
        
    return count, class_name