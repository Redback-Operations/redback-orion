from sahi.predict import get_sliced_prediction,get_prediction
from sahi import AutoDetectionModel
import cv2
from ultralytics import YOLO
import os
import math

class BOX:
    def __init__(self,minx,miny,maxx,maxy):
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
    def __str__(self):
        return f"minx: {self.minx}, miny: {self.miny}, maxx: {self.maxx}, maxy: {self.maxy}"
    def __repr__(self):
        return f"minx: {self.minx}, miny: {self.miny}, maxx: {self.maxx}, maxy: {self.maxy}"

def get_model_with_sahi_cuda(model_path):
    detection_model = AutoDetectionModel.from_pretrained(
        model_type='yolov8',
        model_path=model_path,
        confidence_threshold=0.3,
        device='cpu'
    )
    return detection_model

def get_model_with_sahi_cpu(model_path):
    detection_model = AutoDetectionModel.from_pretrained(
        model_type='yolov8',
        model_path=model_path,
        confidence_threshold=0.3,
        device='cpu'
    )
    return detection_model
def draw_box(image,x1,y1,x2,y2,cato,color=(0, 0, 255), thickness=1):
    cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
    cv2.putText(image, cato, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    return image
def draw_bbox_sahi(image, BoudingBox, color=(0, 0, 255), thickness=1):
    bbox = BoudingBox.bbox
    cato = BoudingBox.category.name
    x1, y1, x2, y2 = int(bbox.minx), int(bbox.miny), int(bbox.maxx), int(bbox.maxy)
    
    return draw_box(image,x1,y1,x2,y2,cato,color,thickness)

def draw_bbox_yolo(image, box,cato, color=(0, 255,0), thickness=1):
    xcod = box.xyxy
    x1, y1, x2, y2 = int(xcod[0][0]), int(xcod[0][1]), int(xcod[0][2]), int(xcod[0][3])
    return draw_box(image,x1,y1,x2,y2,cato,color,thickness)

def merge_img_horizen(img1,img2):
    return cv2.hconcat([img1, img2])

def calculate_iou(bbox1, bbox2):
    x1 = max(bbox1.minx, bbox2.minx)
    y1 = max(bbox1.miny, bbox2.miny)
    x2 = min(bbox1.maxx, bbox2.maxx)
    y2 = min(bbox1.maxy, bbox2.maxy)
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (bbox1.maxx - bbox1.minx) * (bbox1.maxy - bbox1.miny)
    area2 = (bbox2.maxx - bbox2.minx) * (bbox2.maxy - bbox2.miny)
    union = area1 + area2 - intersection
    iou = intersection / union
    return iou

def merge_overlapping_boxes(object_prediction_list):
    merged_predictions = []
    for i in range(len(object_prediction_list)):
        bbox1 = object_prediction_list[i].bbox
        merged = False
        for j in range(i+1, len(object_prediction_list)):
            bbox2 = object_prediction_list[j].bbox
            if calculate_iou(bbox1, bbox2) > 0.1:
                merged = True
                break
        if not merged:
            merged_predictions.append(object_prediction_list[i])
    return merged_predictions


def get_sahi_prediction(image_path, detection_model, slice_height=256, slice_width=256, overlap_height_ratio=0.2, overlap_width_ratio=0.2):
    result = get_sliced_prediction(
        image_path,
        detection_model,
        slice_height=slice_height,
        slice_width=slice_width,
        overlap_height_ratio=overlap_height_ratio,
        overlap_width_ratio=overlap_width_ratio,
    )
    res = cv2.imread(image_path)
    
    object_prediction_list = result.object_prediction_list
    object_prediction_list = merge_overlapping_boxes(object_prediction_list)
    cv2.putText(res, f'sahi: detected {len(object_prediction_list)} items.', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    for object_prediction in object_prediction_list:
        res = draw_bbox_sahi(res, object_prediction)

    return res


def get_yolo_prediction(image_path, detection_model):
    result = get_prediction(image_path,detection_model)
    res = cv2.imread(image_path)
    object_prediction_list = result.object_prediction_list
    object_prediction_list = merge_overlapping_boxes(object_prediction_list)
    cv2.putText(res, f'only yolo: detected {len(object_prediction_list)} items.', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    for object_prediction in object_prediction_list:
        res = draw_bbox_sahi(res, object_prediction)
    return res

def test_performance(input_path,output_path,detection_model,slice_height=256, slice_width=256, overlap_height_ratio=0.2, overlap_width_ratio=0.2):
    res_sahi = get_sahi_prediction(
        input_path,detection_model,slice_height,slice_width,overlap_height_ratio
    )
    
    res_yolo = get_yolo_prediction(
        input_path,detection_model
    )
    res = merge_img_horizen(res_sahi,res_yolo)

    cv2.imwrite(output_path,res)



def get_video_sahi_prediction(video_path, detection_model, slice_height=256, slice_width=256, overlap_height_ratio=0.2, overlap_width_ratio=0.2, output_video_path=None):
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Error opening video file: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if output_video_path:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break 

        result = get_sliced_prediction(
            frame,
            detection_model,
            slice_height=slice_height,
            slice_width=slice_width,
            overlap_height_ratio=overlap_height_ratio,
            overlap_width_ratio=overlap_width_ratio,
        )

        object_prediction_list = result.object_prediction_list
        object_prediction_list = merge_overlapping_boxes(object_prediction_list)
        
        cv2.putText(frame, f'SAHI: detected {len(object_prediction_list)} items.', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        for object_prediction in object_prediction_list:
            frame = draw_bbox_sahi(frame, object_prediction)

        cv2.imshow('Frame', frame)

        if output_video_path:
            out.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    if output_video_path:
        out.release()
    cv2.destroyAllWindows()


def get_center(bbox):
    x1, y1, x2, y2 = int(bbox.minx), int(bbox.miny), int(bbox.maxx), int(bbox.maxy)
    return (int((x1+x2)/2),int((y1+y2)/2))

def dis(c1,c2):
    if c1 is None or c2 is None:
        return 0
    return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

def trans_to_bbox(box):
    xcod = box.xyxy
    x1, y1, x2, y2 = int(xcod[0][0]), int(xcod[0][1]), int(xcod[0][2]), int(xcod[0][3])
    return BOX(minx=x1,miny=y1,maxx=x2,maxy=y2)

#If the model do not detect the object, then use SAHI
def get_video_prediction_with_fallback(video_path, detection_model,yolo_model,  slice_height=256, slice_width=256, overlap_height_ratio=0.2, overlap_width_ratio=0.2, output_video_path=None,dis_thres=100):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Error opening video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if output_video_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
    yolocnt = 0
    sahicnt = 0
    zerocnt = 0
    last_pos = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break  
        print(f"frame {yolocnt + sahicnt+zerocnt}")

        
        result_yolo = yolo_model.predict(frame)
        result_yolo = result_yolo[0]

        # If YOLO detects nothing    
        if result_yolo.boxes.shape[0] == 0:  
            # Fall back to SAHI detection
            result_sahi = get_sliced_prediction(
                frame,
                detection_model,
                slice_height=slice_height,
                slice_width=slice_width,
                overlap_height_ratio=overlap_height_ratio,
                overlap_width_ratio=overlap_width_ratio,
            )
            
            object_prediction_list = result_sahi.object_prediction_list

            if len(object_prediction_list) == 0:
                cv2.putText(frame, f'SAHI: detected 0 items.', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                zerocnt += 1
            else:
                cv2.putText(frame, f'SAHI: detected {len(object_prediction_list)} items.', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                for object_prediction in object_prediction_list:
                    frame = draw_bbox_sahi(frame, object_prediction)
                sahicnt += 1
                last_pos = get_center(object_prediction_list[0].bbox)
                                                                                                                
        else:
            yolocnt += 1
            tmp_boxes = []
            for box in result_yolo.boxes:
                if dis(last_pos,get_center(trans_to_bbox(box))) < dis_thres:
                    tmp_boxes.append(box)
            for box in result_yolo.boxes:
                frame = draw_bbox_yolo(frame, box,"football")
            if(len(tmp_boxes) > 0):
                last_pos = get_center(trans_to_bbox(tmp_boxes[0]))

        if output_video_path:
            out.write(frame)
        cv2.imwrite(os.path.join("out_img",f'{sahicnt+yolocnt+zerocnt}.jpg'),frame)

    print("over")
    print(f"yolocnt: {yolocnt}")
    print(f"sahicnt: {sahicnt}")
    print(f"zerocnt: {zerocnt}")
    cap.release()
    if output_video_path:
        out.release()
    # cv2.destroyAllWindows()