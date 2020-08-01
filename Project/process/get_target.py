import time
import cv2
import numpy as np
import tensorflow as tf
from process.yolov3_tf2.models import YoloV3
from process.yolov3_tf2.dataset import transform_images, load_tfrecord_dataset
from process.yolov3_tf2.utils import draw_outputs, draw_output
from bson.objectid import ObjectId
import os

from sklearn.cluster import KMeans

from process.init import yolo, class_names
size = 416


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

        orb = cv2.ORB_create(5000, 2.0)
        try:
            keypoints_train, descriptors_train = orb.detectAndCompute(train_img, None)
            keypoints_query, descriptors_query = orb.detectAndCompute(query_img, None)
            
            total_keys = len(keypoints_train)
            
            if(descriptors_query is not None):
                bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck = False)
                matches = bf.match(descriptors_train, descriptors_query)
                matches = sorted(matches, key = lambda x : x.distance)
                matched_keys = len(matches)

                success = (100*matched_keys)/total_keys
            else:
                success = 0
        except:
            success = 0  
            print("orb error")      

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


# ./static/videos/output.avi
def getTarget(videos_path, videos_filename, target, caseID, client):

    status = 0
    record = []
    videoID = []
    videos_count = 0
    total_videos = len(videos_filename)

    for video in videos_filename:

        vid_path = videos_path + "/" + video

        vid_info = video.split(".")[0].split("_")

        vid_id = int(vid_info[0])
        vid_time = vid_info[1]
        vid_location = vid_info[2]

        vid_time = vid_time.split("-")

        vid_year = int(vid_time[0])
        vid_month = int(vid_time[1])
        vid_day = int(vid_time[2])
        vid_hour = int(vid_time[3])
        vid_min = int(vid_time[4])

        vid_location = vid_location.split("-")

        vid_lat_in = vid_location[0]
        vid_long_in = vid_location[1]

        vid_lat_in = vid_lat_in.split("=")
        vid_long_in = vid_long_in.split("=")

        vid_lat = float(vid_lat_in[0] + "." + vid_lat_in[1])
        vid_long = float(vid_long_in[0] + "." + vid_long_in[1])

        videoID_rec = {
            "id": vid_id,
            "filename": video,
            "lat": vid_lat,
            "long": vid_long
        }
        
        videoID.append(videoID_rec)

        def isLeap(yr):
            if (yr % 4) == 0: 
                if (yr % 100) == 0: 
                    if (yr % 400) == 0: 
                        return True
                    else: 
                        return False
                else: 
                    return True
            else: 
                return False

        def currTime(min_passed):
            remainder = min_passed%60
            hour_passed = int((min_passed-remainder)/60)
            min_passed = remainder

            remainder = hour_passed%24
            day_passed = int((hour_passed-remainder)/24)
            hour_passed = remainder

            if(min_passed+vid_min >= 60):
                cur_min = (min_passed+vid_min) - 60
                hour_passed += 1
            else:
                cur_min = min_passed+vid_min

            if(hour_passed+vid_hour >= 24):
                cur_hour = (hour_passed+vid_hour) - 24
                day_passed += 1
            else:
                cur_hour = hour_passed+vid_hour

            cur_day = vid_day
            cur_month = vid_month
            cur_year = vid_year

            while day_passed:
                m = cur_month
                if(m==1 or m==3 or m==5 or m==7 or m==8 or m==10 or m==12):
                    m_days = 31
                elif(m==4 or m==6 or m==9 or m==11):
                    m_days = 30
                elif(m==2):
                    if(isLeap(cur_year)):
                        m_days = 29
                    else:
                        m_days = 28
                if(day_passed > m_days-cur_day):
                    day_passed -= (m_days-cur_day)
                    day_passed -= 1
                    cur_day = 1
                    cur_month += 1
                else:
                    cur_day += day_passed
                    day_passed = 0  
                if(cur_month >= 13):
                    cur_year += 1
                    cur_month = 1

            return cur_year, cur_month, cur_day, cur_hour, cur_min


        vid = cv2.VideoCapture(vid_path)

        output = "./static/videos/{}/output/{}.avi".format(caseID,video.split(".")[0])

        vid_fps = int(vid.get(cv2.CAP_PROP_FPS))
        width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        codec = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output, codec, vid_fps, (width, height))
        
        fps = 0.0
        count = 0
        frames_count = 0
        frames_track = 0
        skip_frame = 0
        vid_fpm = 60*vid_fps

        while True:
            _, img = vid.read()

            if img is None:
                count+=1
                if count < 3:
                    continue
                else:
                    print("Processing of " + video + " has successfully completed...")
                    break

            frames_count += 1
            frames_track += 1

            if(frames_track == vid_fpm):
                frames_track = 0

            if(skip_frame > 0):
                skip_frame -= 1
                continue    

            img_in = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
            img_in = tf.expand_dims(img_in, 0)
            img_in = transform_images(img_in, size)

            t1 = time.time()
            boxes, scores, classes, nums = yolo.predict(img_in)

            bags = []
            for i in range(nums[0]):
                temp_class = class_names[int(classes[0][i])]
                if (temp_class=="suitcase" or temp_class=="handbag" or temp_class=="backpack"):
                    box = []
                    [box.append(float(i)) for i in np.array(boxes[0][i])]
                    bag = {
                        "confidence": float(np.array(scores[0][i])),
                        "box": box
                    }
                    bags.append(bag) 
            
            # img = cv2.cvtColor(raw_img.numpy(), cv2.COLOR_RGB2BGR)
            h = img.shape[0]
            w = img.shape[1]

            if(not len(bags) > 0):
                continue

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
                # Finding the side of a bag with best match
                for j in range(len(sides)):
                    v1 = (img_orb[j]['success']*30)/100
                    v2 = (img_color[j]['success']*70)/100
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
        
            if(not score == -1):  # got the bag with best match
                best_bag_box = bags[best_bag_index]['box']
                img = draw_output(img, best_bag_box)
                # skip_frame = vid_fpm - frames_track
                curr_year, curr_month, curr_day, curr_hour, curr_min = currTime(int((frames_count/vid_fps)/60))

                found = 0
                year_index = -1
                for i in range(len(record)):
                    if(record[i]['year'] == curr_year):
                        found = 1
                        year_index = i
                        break

                if(not found):
                    rec = {
                        "year": curr_year,
                        "months": [{
                            "month": curr_month,
                            "days": [{
                                "day": curr_day,
                                "hours": [{
                                    "hour": curr_hour,
                                    "minutes": [{
                                        "minute": curr_min,
                                        "vid": [vid_id]
                                    }]
                                }]
                            }]
                        }]
                    }
                    record.append(rec)
                else:
                    found = 0
                    months = record[year_index]['months']
                    month_index = -1
                    for i in range(len(months)):
                        if(months[i]['month'] == curr_month):
                            found = 1
                            month_index = i
                            break
                    if(not found):
                        rec = {
                            "month": curr_month,
                            "days": [{
                                "day": curr_day,
                                "hours": [{
                                    "hour": curr_hour,
                                    "minutes": [{
                                        "minute": curr_min,
                                        "vid": [vid_id]
                                    }]
                                }]
                            }]
                        } 
                        record[year_index]['months'].append(rec)
                    else:
                        found = 0
                        days = record[year_index]['months'][month_index]['days']
                        day_index = -1
                        for i in range(len(days)):
                            if(days[i]['day'] == curr_day):
                                found = 1
                                day_index = i
                                break
                        if(not found):
                            rec = {
                                "day": curr_day,
                                "hours": [{
                                    "hour": curr_hour,
                                    "minutes": [{
                                        "minute": curr_min,
                                        "vid": [vid_id]
                                    }]
                                }]
                            }  
                            record[year_index]['months'][month_index]['days'].append(rec)
                        else:
                            found = 0
                            hours = record[year_index]['months'][month_index]['days'][day_index]['hours']
                            hour_index = -1
                            for i in range(len(hours)):
                                if(hours[i]['hour'] == curr_hour):
                                    found = 1
                                    hour_index = i 
                                    break
                            if(not found):
                                rec = {
                                    "hour": curr_hour,
                                    "minutes": [{
                                        "minute": curr_min,
                                        "vid": [vid_id]
                                    }]
                                }
                                record[year_index]['months'][month_index]['days'][day_index]['hours'].append(rec)
                            else:
                                found = 0
                                minutes = record[year_index]['months'][month_index]['days'][day_index]['hours'][hour_index]['minutes']
                                minute_index = -1
                                for i in range(len(minutes)):
                                    if(minutes[i]['minute'] == curr_min):
                                        found = 1
                                        minute_index = i 
                                        break
                                if(not found):
                                    rec = {
                                        "minute": curr_min,
                                        "vid": [vid_id]
                                    }
                                    record[year_index]['months'][month_index]['days'][day_index]['hours'][hour_index]['minutes'].append(rec)
                                else:
                                    record[year_index]['months'][month_index]['days'][day_index]['hours'][hour_index]['minutes'][minute_index]['vid'].append(vid_id)    

            # fps  = ( fps + (1./(time.time()-t1)) ) / 2

            # print("FPS: " + str(fps))
            out.write(img)

        videos_count += 1
        status = int((videos_count/total_videos)*100)

        status_update = {
            "analysis": {
                "status": status
            }
        }

        client.db.cases.update_one({'_id': ObjectId(caseID)}, {'$set': status_update})
        print("status : " + str(status) + "%")

    update = {
        "analysis": {
            "status": -1,
            "record": record,
            "videoID": videoID
        }
    }

    client.db.cases.update_one({'_id': ObjectId(caseID)}, {'$set': update})
