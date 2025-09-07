from ultralytics import YOLO
import cv2
import numpy as np


model = YOLO('Player_Tracking/detect/train/weights/best.pt') 

image_path = r'D:\SIT220\Player_Tracking\微信图片_20241129200946.jpg'  
image = cv2.imread(image_path)

results = model(image) 


for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy.tolist()[0] 
            conf = box.conf.item() 
            cls = int(box.cls.item()) 

            if cls == 0:
                label = f'Football {conf:.2f}'
  
                cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                cv2.putText(image, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)


cv2.imwrite('output_image.jpg', image)
cv2.imshow('Detected Image', image) 
cv2.waitKey(0)
cv2.destroyAllWindows()
