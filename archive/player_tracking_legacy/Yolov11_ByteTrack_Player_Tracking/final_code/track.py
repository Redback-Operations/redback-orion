import cv2
import numpy as np
import json
from ultralytics import YOLO
from typing import Dict, List

class Tracking:
    def __init__(self, model_path: str, confidence_threshold: float = 0.3):
        self.yolo_model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
    
    def __call__(self, video_path: str, output_video: str = None, save_json: bool = True) -> Dict:
        return self.process_video(video_path, output_video, save_json)
    
    def calculate_iou(self, box1: List[float], box2: List[float]) -> float:
        x1, y1, x2, y2 = max(box1[0], box2[0]), max(box1[1], box2[1]), min(box1[2], box2[2]), min(box1[3], box2[3])
        if x2 <= x1 or y2 <= y1:
            return 0.0
        intersection = (x2 - x1) * (y2 - y1)
        union = (box1[2] - box1[0]) * (box1[3] - box1[1]) + (box2[2] - box2[0]) * (box2[3] - box2[1]) - intersection
        return intersection / union if union > 0 else 0.0
    
    def filter_overlapping_detections(self, boxes) -> List[int]:
        if boxes is None or len(boxes) == 0:
            return []
        
        xyxy = boxes.xyxy.cpu().numpy()
        conf = boxes.conf.cpu().numpy()
        keep_indices = []
        
        for i in range(len(boxes)):
            if conf[i] < self.confidence_threshold:
                continue
            
            keep = True
            for j in range(len(boxes)):
                if i == j:
                    continue
                if self.calculate_iou(xyxy[i], xyxy[j]) > 0.7 and conf[i] < conf[j]:
                    keep = False
                    break
            if keep:
                keep_indices.append(i)
        
        return keep_indices
    
    def process_video(self, video_path: str, output_path: str = None, save_json: bool = True) -> Dict:
        cap = cv2.VideoCapture(video_path)
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        out = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        tracking_data = {
            "video_info": {
                "duration": total_frames / fps,
                "fps": fps,
                "total_frames": total_frames,
                "resolution": [width, height]
            },
            "tracking_results": []
        }
        
        frame_number = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            results = self.yolo_model.track(frame, persist=True, tracker="bytetrack.yaml")
            boxes = results[0].boxes
            
            if boxes is not None and len(boxes) > 0:
                keep_indices = self.filter_overlapping_detections(boxes)
                if keep_indices:
                    boxes = boxes[keep_indices]
                    results[0].boxes = boxes
            
            frame_data = {
                "frame_number": frame_number + 1,
                "timestamp": round(frame_number / fps, 3),
                "players": []
            }
            
            if boxes is not None and len(boxes) > 0:
                xyxy = boxes.xyxy.cpu().numpy()
                conf = boxes.conf.cpu().numpy()
                ids = boxes.id.cpu().numpy() if boxes.id is not None else None
                
                for i in range(len(boxes)):
                    bbox = xyxy[i]
                    confidence = float(conf[i])
                    player_id = int(ids[i]) if ids is not None else i + 1
                    
                    player_data = {
                        "player_id": player_id,
                        "bbox": {"x1": int(bbox[0]), "y1": int(bbox[1]), "x2": int(bbox[2]), "y2": int(bbox[3])},
                        "center": {"x": int((bbox[0] + bbox[2]) / 2), "y": int((bbox[1] + bbox[3]) / 2)},
                        "confidence": round(confidence, 2),
                        "width": int(bbox[2] - bbox[0]),
                        "height": int(bbox[3] - bbox[1])
                    }
                    
                    frame_data["players"].append(player_data)
            
            tracking_data["tracking_results"].append(frame_data)
            
            if output_path:
                annotated_frame = results[0].plot()
                out.write(annotated_frame)
            
            frame_number += 1
                
        cap.release()
        if out:
            out.release()
        
        if save_json:
            json_output_path = video_path.rsplit('.', 1)[0] + "_tracking.json"
            with open(json_output_path, 'w') as f:
                json.dump(tracking_data, f, indent=2)
        
        return tracking_data


def main():
    # Configuration
    model_path = '/home/huylx/workspace/ultralytics/runs/detect/current_best/weights/best.pt'
    video_path = 'Shorts/short_brisbane_v_westcoast.mp4'
    output_path = video_path.rsplit('.', 1)[0] + "_separated_tracking_ocr.mp4"
    
    # Initialize tracking module
    track_module = Tracking(
        model_path=model_path,
        confidence_threshold=0.3
    )
    
    # Process video with output video and JSON saving
    results = track_module(
        video_path=video_path,
        output_video=output_path,
        save_json=True
    )

if __name__ == "__main__":
    main()