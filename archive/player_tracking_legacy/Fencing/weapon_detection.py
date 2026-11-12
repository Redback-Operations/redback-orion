#!/usr/bin/env python
# coding: utf-8

# In[1]:


import cv2
from ultralytics import YOLO


# In[2]:


model = YOLO('weapon_model/best_weapon.pt')


# In[1]:


def process_frame_for_weapon(frame):
    results = model.predict(frame)
    for result in results:
        detections = result.boxes
        for i in range(detections.xyxy.shape[0]):
            x1, y1, x2, y2 = detections.xyxy[i][:4].int().tolist()
            confidence = detections.conf[i].item()
            label_id = detections.cls[i].int().item()
            label = model.names[label_id]

            if label == 'weapon':
                border_color = (0, 255, 0)
                border_thickness = 5

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), border_color, border_thickness)

                # Label the bounding box
                cv2.putText(frame, f'{label} {confidence:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, border_color, 2)


# In[ ]:




