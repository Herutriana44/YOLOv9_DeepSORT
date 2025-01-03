# -*- coding: utf-8 -*-
"""YOLOv9_DeepSORT_2_Direction.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1RTS6umFFUoq7xbVaFl-FGGqAaOZfrEuI

# Clone the Github Repo & Install all the Dependencies
"""

!git clone https://github.com/Herutriana44/Vehicle-Counting-Detection-Speed-Detection-YoloV9-DeepSort

# Commented out IPython magic to ensure Python compatibility.
!git clone https://github.com/sujanshresstha/YOLOv9_DeepSORT.git
# %cd YOLOv9_DeepSORT
!pip install -q -r requirements.txt

# Commented out IPython magic to ensure Python compatibility.
 !git clone https://github.com/WongKinYiu/yolov9.git
#  %cd yolov9
 !pip install -q -r requirements.txt

!mkdir -p weights
!wget -P weights https://github.com/WongKinYiu/yolov9/releases/download/v0.1/yolov9-e.pt
!wget -P weights https://github.com/WongKinYiu/yolov9/releases/download/v0.1/yolov9-c.pt

from IPython.display import HTML
from base64 import b64encode
def play_video(filename):
  html = ''
  video = open(filename,'rb').read()
  src = 'data:video/mp4;base64,' + b64encode(video).decode()
  html += fr'<video width=900 controls autoplay loop><source src="%s" type="video/mp4"></video>' % src
  return HTML(html)

"""# Parameters"""

# Commented out IPython magic to ensure Python compatibility.
# %ls

# SOURCE_VIDEO_PATH = "/content/YOLOv9_DeepSORT/data/ped_track.mp4"
SOURCE_VIDEO_PATH = "/content/Vehicle-Counting-Detection-Speed-Detection-YoloV9-DeepSort/Road traffic video for object recognition - short.mp4"
OUTPUT_VIDEO_PATH = "/content/output.mp4"
BLUR_ID = None
CONF = 0.6
CLASS_ID = None
# arah bawah ke atas
area1 = [(912,716),(916,1052),(20,1052),(20,712)]
area1_color = (255,255, 0)
area1_txt = "Area 1"
area2 = [(944,438),(944,564),(512,564),(512,438)]
area2_color = (255,0,255)
area2_txt = "Area 2"
# arah atas ke bawah
area3 = [(1350,454),(1350,592),(982,592),(982,454)]
area3_color = (0,255, 0)
area3_txt = "Area 3"
area4 = [(1842,706),(1842,1042),(1024,1042),(1024,706)]
area4_color = (255,0,0)
area4_txt = "Area 4"
count_v = 0
vihicle_run_time = {}
vihicle_in_roi = {}
vihicle_run_time2 = {}
vihicle_in_roi2 = {}

"""# Codes"""

import cv2
import torch
import time
import colorsys
import numpy as np
from absl import app, flags
from absl.flags import FLAGS
from deep_sort_realtime.deepsort_tracker import DeepSort
from models.common import DetectMultiBackend, AutoShape
import time

def draw_corner_rect(img, bbox, line_length=30, line_thickness=5, rect_thickness=1,
                     rect_color=(255, 0, 255), line_color=(0, 255, 0)):
    x, y, w, h = bbox
    x1, y1 = x + w, y + h

    if rect_thickness != 0:
        cv2.rectangle(img, bbox, rect_color, rect_thickness)

    # Top Left  x, y
    cv2.line(img, (x, y), (x + line_length, y), line_color, line_thickness)
    cv2.line(img, (x, y), (x, y + line_length), line_color, line_thickness)

    # Top Right  x1, y
    cv2.line(img, (x1, y), (x1 - line_length, y), line_color, line_thickness)
    cv2.line(img, (x1, y), (x1, y + line_length), line_color, line_thickness)

    # Bottom Left  x, y1
    cv2.line(img, (x, y1), (x + line_length, y1), line_color, line_thickness)
    cv2.line(img, (x, y1), (x, y1 - line_length), line_color, line_thickness)

    # Bottom Right  x1, y1
    cv2.line(img, (x1, y1), (x1 - line_length, y1), line_color, line_thickness)
    cv2.line(img, (x1, y1), (x1, y1 - line_length), line_color, line_thickness)

    return img

cap = cv2.VideoCapture(SOURCE_VIDEO_PATH)

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
# video writer objects
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(OUTPUT_VIDEO_PATH, fourcc, fps, (frame_width, frame_height))

# Initialize the DeepSort tracker
tracker = DeepSort(max_age=50)
# select device (CPU or GPU)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using:{device}")
# Load YOLO model
model = DetectMultiBackend(weights='./weights/yolov9-c.pt',device=device, fuse=True)
model = AutoShape(model)

# Load the COCO class labels
classes_path = "../configs/coco.names"
with open(classes_path, "r") as f:
  class_names = f.read().strip().split("\n")

# Create a list of random colors to represent each class
np.random.seed(42)
colors = np.random.randint(0, 255, size=(len(class_names), 3))

# FPS calculation variables
frame_count = 0
start_time = time.time()

while True:
  ret, frame = cap.read()
  if not ret:
      break

  frame = cv2.polylines(frame, [np.array(area1, np.int32)], True, area1_color, 2)
  cv2.putText(frame, area1_txt, (area1[0][0], area1[0][1]), 0, 0.75, area1_color, 2)
  frame = cv2.polylines(frame, [np.array(area2, np.int32)], True, area2_color, 2)
  cv2.putText(frame, area2_txt, (area2[0][0], area2[0][1]), 0, 0.75, area2_color, 2)
  frame = cv2.polylines(frame, [np.array(area4, np.int32)], True, area4_color, 2)
  cv2.putText(frame, area4_txt, (area4[0][0], area4[0][1]), 0, 0.75, area4_color, 2)
  frame = cv2.polylines(frame, [np.array(area3, np.int32)], True, area3_color, 2)
  cv2.putText(frame, area3_txt, (area3[0][0], area3[0][1]), 0, 0.75, area3_color, 2)

  cv2.putText(frame, "count : "+str(count_v),(50,50),0, 0.75, (255,255,255),2)
  # Run model on each frame
  start_time = time.time()

  results = model(frame)
  detect = []
  for det in results.pred[0]:
    label, confidence, bbox = det[5], det[4], det[:4]
    x1, y1, x2, y2 = map(int, bbox)
    class_id = int(label)

    # Filter out weak detections by confidence threshold and class_id
    if CLASS_ID is None:
        if confidence < CONF:
            continue
    else:
        if class_id != CLASS_ID or confidence < CONF:
            continue

    detect.append([[x1, y1, x2 - x1, y2 - y1], confidence, class_id])

  tracks = tracker.update_tracks(detect, frame=frame)

  for track in tracks:
    if not track.is_confirmed():
      continue
    track_id = track.track_id
    ltrb = track.to_ltrb()
    class_id = track.get_det_class()
    x1, y1, x2, y2 = map(int, ltrb)

    color = colors[class_id]
    B, G, R = map(int, color)
    text = f"{track_id} - {class_names[class_id]}"

    frame = draw_corner_rect(frame, (x1, y1, x2 - x1, y2 - y1), line_length=15, line_thickness=3, rect_thickness=1, rect_color=(B, G, R), line_color=(R, G, B))
    cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 2)
    cv2.rectangle(frame, (x1 - 1, y1 - 20), (x1 + len(text) * 10, y1), (B, G, R), -1)
    cv2.putText(frame, text, (x1 + 5, y1 - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Apply Gaussian Blur
    if BLUR_ID is not None and class_id == BLUR_ID:
      if 0 <= x1 < x2 <= frame.shape[1] and 0 <= y1 < y2 <= frame.shape[0]:
        frame[y1:y2, x1:x2] = cv2.GaussianBlur(frame[y1:y2, x1:x2], (99, 99), 3)

    centerX = (x1+x2)/2
    centerY = (y1+y2)/2
    result = cv2.pointPolygonTest(np.array(area1, np.int32),(int(centerX),int(centerY)), False) # ketika kendaraan melewati area 1 bawah ke atas

    if result >= 0:
        vihicle_in_roi[track_id] = time.time()

    if track_id in vihicle_in_roi:
        result = cv2.pointPolygonTest(np.array(area2, np.int32),(int(centerX),int(centerY)), False)  # ketika kendaraan melewati area 2 bawah ke atas
        if result >= 0:
          elapsed_time = time.time() - vihicle_in_roi[track_id]

          if track_id not in vihicle_run_time:
            vihicle_run_time[track_id] = elapsed_time
            count_v += 1

          if track_id in vihicle_run_time:
            elapsed_time = vihicle_run_time[track_id]


          distance = 50
          speed_ms = distance / elapsed_time
          speed_kh = speed_ms * 3.6
          speed_txt = " Speed : " + str(int(speed_kh)) + "Km/h"
          #speed_txt = " E.T : " + str(elapsed_time)

          color = colors[class_id]
          B, G, R = map(int, color)
          text = f"{track_id} - {class_names[class_id]} - {str(speed_txt)}"

          frame = draw_corner_rect(frame, (x1, y1, x2 - x1, y2 - y1), line_length=15, line_thickness=3, rect_thickness=1, rect_color=(B, G, R), line_color=(R, G, B))
          cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 2)
          cv2.rectangle(frame, (x1 - 1, y1 - 20), (x1 + len(text) * 10, y1), (B, G, R), -1)
          cv2.putText(frame, text, (x1 + 5, y1 - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

          # Apply Gaussian Blur
          if BLUR_ID is not None and class_id == BLUR_ID:
            if 0 <= x1 < x2 <= frame.shape[1] and 0 <= y1 < y2 <= frame.shape[0]:
              frame[y1:y2, x1:x2] = cv2.GaussianBlur(frame[y1:y2, x1:x2], (99, 99), 3)

    result2 = cv2.pointPolygonTest(np.array(area3, np.int32),(int(centerX),int(centerY)), False) # ketika kendaraan melewati area 4 atas ke bawah
    if result2 >= 0:
        vihicle_in_roi2[track_id] = time.time()

    if track_id in vihicle_in_roi2:
        result2 = cv2.pointPolygonTest(np.array(area4, np.int32),(int(centerX),int(centerY)), False)  # ketika kendaraan melewati area 3 atas ke bawah
        if result2 >= 0:
          elapsed_time = time.time() - vihicle_in_roi2[track_id]

          if track_id not in vihicle_run_time2:
            vihicle_run_time2[track_id] = elapsed_time
            count_v += 1

          if track_id in vihicle_run_time2:
            elapsed_time = vihicle_run_time2[track_id]


          distance = 50
          speed_ms = distance / elapsed_time
          speed_kh = speed_ms * 3.6
          speed_txt = " Speed : " + str(int(speed_kh)) + "Km/h"
          #speed_txt = " E.T : " + str(elapsed_time)

          # draw bbox on screen

          color = colors[class_id]
          B, G, R = map(int, color)
          text = f"{track_id} - {class_names[class_id]} - {str(speed_txt)}"

          frame = draw_corner_rect(frame, (x1, y1, x2 - x1, y2 - y1), line_length=15, line_thickness=3, rect_thickness=1, rect_color=(B, G, R), line_color=(R, G, B))
          cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 2)
          cv2.rectangle(frame, (x1 - 1, y1 - 20), (x1 + len(text) * 10, y1), (B, G, R), -1)
          cv2.putText(frame, text, (x1 + 5, y1 - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

          # Apply Gaussian Blur
          if BLUR_ID is not None and class_id == BLUR_ID:
            if 0 <= x1 < x2 <= frame.shape[1] and 0 <= y1 < y2 <= frame.shape[0]:
              frame[y1:y2, x1:x2] = cv2.GaussianBlur(frame[y1:y2, x1:x2], (99, 99), 3)

  writer.write(frame)

  frame_count += 1
  if frame_count % 30 == 0:
    elapsed_time = time.time() - start_time
    fps_calc = frame_count / elapsed_time
    print(f"FPS: {fps_calc:.2f}")

  if cv2.waitKey(1) & 0xFF == ord('q'):
      break

cap.release()
writer.release()

!ffmpeg -i /content/output.mp4 -vcodec libx264 /content/test3_1.mp4

"""# Play output video"""

play_video("/content/test3_1.mp4")

# download file test3_1.mp4
from google.colab import files
files.download("/content/test3_1.mp4")

!zip /content/YOLOv9_DeepSORT.zip -r /content/YOLOv9_DeepSORT/

# download file test3_1.mp4
from google.colab import files
files.download("/content/YOLOv9_DeepSORT.zip")

