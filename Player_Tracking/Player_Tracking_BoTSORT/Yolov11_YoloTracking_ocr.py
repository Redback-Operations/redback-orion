import cv2
from ultralytics import YOLO
import numpy as np
import json

def calculate_iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    if x2 <= x1 or y2 <= y1:
        return 0.0
    
    intersection = (x2 - x1) * (y2 - y1)
    
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = box1_area + box2_area - intersection
    
    if union == 0:
        return 0.0
    
    return intersection / union

# ✅ Use working model
model = YOLO('yolov8n.pt')

# 🎥 Input video
video_path = 'GC_Carlton_Original.mp4'
output_path = "output_tracked.mp4"

cap = cv2.VideoCapture(video_path)

fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

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
    
    results = model.track(
        frame,
        persist=True,
        tracker="botsort.yaml"
    )
    
    boxes = results[0].boxes
    
    if boxes is not None and len(boxes) > 0:
        xyxy = boxes.xyxy.cpu().numpy()
        conf = boxes.conf.cpu().numpy()
        cls = boxes.cls.cpu().numpy()
        
        keep_indices = []
        
        for i in range(len(boxes)):
            keep = True
            current_box = xyxy[i]
            current_conf = conf[i]
            current_cls = cls[i]

            if current_conf < 0.3:
                continue
            
            for j in range(len(boxes)):
                if i == j:
                    continue
                    
                compare_box = xyxy[j]
                compare_conf = conf[j]
                compare_cls = cls[j]
                
                iou = calculate_iou(current_box, compare_box)
                
                if iou > 0.7:
                    if current_conf < compare_conf:
                        keep = False
                        break
            
            if keep:
                keep_indices.append(i)
        
        if keep_indices:
            filtered_boxes = boxes[keep_indices]
            results[0].boxes = filtered_boxes
    
    frame_data = {
        "frame_number": frame_number + 1,
        "timestamp": round(frame_number / fps, 3),
        "players": []
    }
    
    final_boxes = results[0].boxes
    
    if final_boxes is not None and len(final_boxes) > 0:
        final_xyxy = final_boxes.xyxy.cpu().numpy()
        final_conf = final_boxes.conf.cpu().numpy()
        final_ids = final_boxes.id.cpu().numpy() if final_boxes.id is not None else None
        
        for i in range(len(final_boxes)):
            bbox = final_xyxy[i]
            confidence = float(final_conf[i])
            player_id = int(final_ids[i]) if final_ids is not None else i + 1
            
            player_data = {
                "player_id": player_id,
                "bbox": {
                    "x1": int(bbox[0]),
                    "y1": int(bbox[1]),
                    "x2": int(bbox[2]),
                    "y2": int(bbox[3])
                },
                "center": {
                    "x": int((bbox[0] + bbox[2]) / 2),
                    "y": int((bbox[1] + bbox[3]) / 2)
                },
                "confidence": round(confidence, 2),
                "width": int(bbox[2] - bbox[0]),
                "height": int(bbox[3] - bbox[1])
            }
            frame_data["players"].append(player_data)
    
    tracking_data["tracking_results"].append(frame_data)
    
    # 🎯 Draw boxes
    annotated_frame = results[0].plot()
    
    # 💾 Save video
    out.write(annotated_frame)
    
    # 🔴 LIVE DISPLAY
    cv2.imshow("Live Tracking", annotated_frame)
    
    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    frame_number += 1

cap.release()
out.release()
cv2.destroyAllWindows()

# 💾 Save JSON
json_output_path = "tracking_data.json"
with open(json_output_path, 'w') as f:
    json.dump(tracking_data, f, indent=2)

print(f"Inference complete! Video saved to: {output_path}")
print(f"Tracking data saved to: {json_output_path}")