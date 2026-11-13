import cv2
from ultralytics import YOLO
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'



model = YOLO('Player_Tracking/detect/train2/weights/best.pt')  


video_path = r"D:\SIT220\Player_Tracking\test3.mp4"  
cap = cv2.VideoCapture(video_path)

fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


out = cv2.VideoWriter('output_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    #results = model(frame) 
    results = model.track(frame, persist=True, show=False, tracker="botsort.yaml")

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy.tolist()[0]  
            conf = box.conf.item()  
            cls = int(box.cls.item()) 

            if cls == 0 and conf>=0.4:
                label = f'Football {conf:.2f}'

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    out.write(frame)
    cv2.imshow('Detection', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
