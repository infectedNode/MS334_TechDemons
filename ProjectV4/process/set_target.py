import cv2
import numpy as np
import os
from collections import Counter
from sklearn.cluster import KMeans

def featureCount(image_path=None):
    image = cv2.imread(image_path)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create(5000, 2.0)

    keypoints, descriptors = orb.detectAndCompute(image, None)

    ln = len(keypoints)

    return ln

def extractColor(image_path):
    image = cv2.imread(image_path)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    modified_image = image.reshape(image.shape[0]*image.shape[1], 3)

    number_of_colors = 7

    clf = KMeans(n_clusters = number_of_colors)
    labels = clf.fit_predict(modified_image)

    counts = Counter(labels)
    center_colors = clf.cluster_centers_

    ordered_colors = [center_colors[i] for i in counts.keys()]
    rgb_colors = [ordered_colors[i] for i in counts.keys()]

    clrs = []
    cnt = 0

    for x in rgb_colors:
        cnt += 1
        clr = {
            "rgb": [int(x[0]), int(x[1]), int(x[2])],
            "lw": None,
            "up": None,
            "id": cnt
        }
        clrs.append(clr)

    return clrs    