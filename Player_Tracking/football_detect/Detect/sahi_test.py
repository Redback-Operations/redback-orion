from sahi import AutoDetectionModel
import cv2
from ultralytics import YOLO
import os
from utils_sahi import get_model_with_sahi_cpu,get_video_prediction_with_fallback

"""
#image_test
yolov11_path='Models/yolov11/weights/best.pt'
model = get_model_with_sahi_cpu(yolov11_path)

input_path='Input/picture1.jpg'
out_path='Output'

out1 = os.path.join(out_path, "small-vehicles1.jpeg")
test_performance(input_path,out1,model,480,480)
"""


video_path = 'Input/test1.mp4'
out_path= 'Output'
output_video_path = os.path.join(out_path, "output_video.mp4")

#yolov8_path='Models/yolov8/weights/best.pt'
yolov11_path='Models/yolov11/weights/best.pt'
sahi_model= get_model_with_sahi_cpu(yolov11_path)
yolo_model = YOLO(yolov11_path)

"""
#video_test_sahi_only
get_video_sahi_prediction(
    video_path, 
    sahi_model, 
    slice_height=512, 
    slice_width=512, 
    overlap_height_ratio=0.1, 
    overlap_width_ratio=0.1, 
    output_video_path=output_video_path
)
"""


#video_test_sahi_partly
get_video_prediction_with_fallback(
    video_path, 
    sahi_model, 
    yolo_model,
    slice_height=480, 
    slice_width=480, 
    overlap_height_ratio=0.2, 
    overlap_width_ratio=0.2, 
    output_video_path=output_video_path
)






