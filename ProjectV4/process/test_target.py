import cv2
import numpy as np
import tensorflow as tf
from process.yolov3_tf2.dataset import transform_images
from process.yolov3_tf2.utils import draw_outputs, draw_output
import os

from sklearn.cluster import KMeans

from process.init import yolo, class_names
size = 416

orb = cv2.ORB_create(5000, 2.0)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)

def hsv(clr):
    r = clr[0]
    g = clr[1]
    b = clr[2]
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100

    return [int(h), int(s), int(v)]

def orb_feature(img, sides, caseID):
    query_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  
    
    outcome = []

    for side in sides:
        image_path = "./static/images/{}/{}.jpg".format(caseID,side)
        train_img = cv2.imread(image_path)
        train_img = cv2.cvtColor(train_img, cv2.COLOR_BGR2GRAY)

        keypoints_train, descriptors_train = orb.detectAndCompute(train_img, None)
        keypoints_query, descriptors_query = orb.detectAndCompute(query_img, None)
        
        total_keys = len(keypoints_train)

        matches = bf.match(descriptors_train, descriptors_query)
        matches = sorted(matches, key = lambda x : x.distance)
        matched_keys = len(matches)

        success = (100*matched_keys)/total_keys

        res = {
            "side": side,
            "success": success
        }
        outcome.append(res)

    return outcome    

def color(img, sides):

    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    modified_image = image.reshape(image.shape[0]*image.shape[1], 3)

    number_of_colors = 7

    clf = KMeans(n_clusters = number_of_colors)
    labels = clf.fit_predict(modified_image)
    center_colors = clf.cluster_centers_

    label_count = [0 for i in range(number_of_colors)]

    for ele in labels:
        label_count[ele] += 1

    hsv_points = []

    for i in range(number_of_colors) :
        hsv_points.append((label_count[i]*100)/len(labels))

    hsv_colors = []
    
    for rgb in center_colors:
        hsv_colors.append(hsv(rgb))

    outcome = []

    print(hsv_points)
    print(hsv_colors)

    for side in sides:
        success = 0.0
        for i in range(len(hsv_colors)):
            test_clr = hsv_colors[i]
            for train_clr in side['colors']:
                if(train_clr['lw'][0]<=test_clr[0] and train_clr['lw'][1]<=test_clr[1] and train_clr['lw'][2]<=test_clr[2] and train_clr['up'][0]>=test_clr[0] and train_clr['up'][1]>=test_clr[1] and train_clr['up'][2]>=test_clr[2]):
                    success += hsv_points[i]
                    break
        
        res = {
            "side": side['side'],
            "success": success
        }
        outcome.append(res)

    return outcome


def testTarget(image, target, caseID):
    raw_img = tf.image.decode_image(open(image, 'rb').read(), channels=3)
    img = tf.expand_dims(raw_img, 0)
    img = transform_images(img, size)

    boxes, scores, classes, nums = yolo(img)

    bags = []
    for i in range(nums[0]):
        box = []
        [box.append(float(i)) for i in np.array(boxes[0][i])]
        bag = {
            "confidence": float(np.array(scores[0][i])),
            "box": box
        }
        bags.append(bag)
    
    img = cv2.cvtColor(raw_img.numpy(), cv2.COLOR_RGB2BGR)
    h = img.shape[0]
    w = img.shape[1]

    if(not len(bags) > 0):
        return img

    bags_img = []

    for bag in bags:
        box = bag['box']
        cropped = img[int(box[1]*h):int(box[3]*h), int(box[0]*w):int(box[2]*w)]
        bags_img.append(cropped)    

    sides = []

    for s in target['sides']:
        sides.append(s['side'])

    bag_score = []   

    for bimg in bags_img:
        img_orb = orb_feature(bimg, sides, caseID)
        img_color = color(bimg, target['sides'])

        max_score = 0.0

        for j in range(len(sides)):
            v1 = (img_orb[j]['success']*30)/100
            v2 = (img_color[j]['success']*70)/100

            print(v1)
            print(v2)
            if((v1+v2) > max_score):
                max_score = v1+v2
        if(max_score < 40):
            bag_score.append(-1)
        else:       
            bag_score.append(max_score)

    best_bag_index = 0
    score = bag_score[0]

    for i in range(len(bag_score)):
        if(bag_score[i] > score):
            score = bag_score[i]
            best_bag_index = i
 
    if(not score == -1):
        best_bag_box = bags[best_bag_index]['box']
        img = draw_output(img, best_bag_box)
        
    return img