from pipeline.data_pipeline import process_tracking_data
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import cv2
from ultralytics import YOLO

model = YOLO('D:/SIT220/detect/train/weights/best.pt')        


video_path = r"D:\SIT220\Player_Tracking\test1.mp4"
cap = cv2.VideoCapture(video_path)


while cap.isOpened():
    success, frame = cap.read()
    if success:
        results = model.track(frame, persist=True, show=True, tracker="botsort.yaml")
        processed_data = process_tracking_data(results)
        print("Processed Data:", processed_data)
        annotated_frame = results[0].plot()
        cv2.imshow("YOLOv8 Tracking", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
