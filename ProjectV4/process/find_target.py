import time
from absl import app, logging
import cv2
import numpy as np
import tensorflow as tf
from process.v4.dataset import transform_images, load_tfrecord_dataset
from process.v4.utils import draw_outputs
import os

from process.init import yolo, class_names
size = 416

def findTarget(image=None, isID=0):
    raw_img = tf.image.decode_image(open(image, 'rb').read(), channels=3)
    img = tf.expand_dims(raw_img, 0)
    img = transform_images(img, size)

    boxes, scores, classes, nums = yolo(img)

    bags = []
    count = 0

    if(isID > 0):
        for i in range(nums[0]):
            temp_class = class_names[int(classes[0][i])]
            if (temp_class=="suitcase" or temp_class=="handbag" or temp_class=="backpack"):
                count += 1

                if(count == isID):
                    box = []
                    [box.append(float(i)) for i in np.array(boxes[0][i])]
                    bag = {
                        "class_name": temp_class,
                        "confidence": float(np.array(scores[0][i])),
                        "box": box
                    }
                    bags.append(bag) 
    else:       
        for i in range(nums[0]):
            temp_class = class_names[int(classes[0][i])]
            if (temp_class=="suitcase" or temp_class=="handbag" or temp_class=="backpack"):
                count += 1
                box = []
                [box.append(float(i)) for i in np.array(boxes[0][i])]
                bag = {
                    "class_name": temp_class,
                    "confidence": float(np.array(scores[0][i])),
                    "box": box
                }
                bags.append(bag)
    
    img = cv2.cvtColor(raw_img.numpy(), cv2.COLOR_RGB2BGR)

    if(isID > 0):
        h = img.shape[0]
        w = img.shape[1]
        img = img[int(box[1]*h):int(box[3]*h), int(box[0]*w):int(box[2]*w)]
    else:    
        img = draw_outputs(img, (boxes, scores, classes, nums), class_names)
        
    return img, count, bags