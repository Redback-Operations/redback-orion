from sahi import AutoDetectionModel
import cv2
from ultralytics import YOLO
import os
from utils_speed import get_video_prediction_with_speed
from utils_sahi import get_model_with_sahi_cpu


video_path = 'Input/test1.mp4'
out_path= 'Output'
output_video_path = os.path.join(out_path, "output_video.mp4")

yolov11_path='Models/yolov11/weights/best.pt'
sahi_model= get_model_with_sahi_cpu(yolov11_path)
yolo_model = YOLO(yolov11_path)


#get football speed 
get_video_prediction_with_speed(
    video_path, 
    sahi_model, 
    yolo_model,
    slice_height=480, 
    slice_width=480, 
    overlap_height_ratio=0.2, 
    overlap_width_ratio=0.2, 
    output_video_path=output_video_path
)
