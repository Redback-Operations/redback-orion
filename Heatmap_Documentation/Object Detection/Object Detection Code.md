import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load YOLO model
yolo_weights = 'yolov4.weights'  # Path to YOLO weights
yolo_config = 'yolov4.cfg'       # Path to YOLO configuration
coco_names = 'coco.names'        # Path to COCO labels

# Load YOLO model
net = cv2.dnn.readNetFromDarknet(yolo_config, yolo_weights)
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
with open(coco_names, 'r') as f:
    classes = [line.strip() for line in f.readlines()]

# Initialize heatmap
heatmap_size = (100, 100)  # Size of the heatmap grid
heatmap = np.zeros(heatmap_size)

# Input video path
video_path = 'stadium_crowd.mp4'  # Path to the video
cap = cv2.VideoCapture(video_path)

# Process the video frame by frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Prepare the frame for YOLO
    height, width, _ = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)
    
    # Collect detected people
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            
            if classes[class_id] == 'person' and confidence > 0.5:  # Detect persons
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                
                # Map detection to heatmap
                x = int((center_x / width) * heatmap_size[1])
                y = int((center_y / height) * heatmap_size[0])
                heatmap[y, x] += 1

    # Visualization (optional)
    heatmap_visual = cv2.resize(heatmap, (width, height))
    heatmap_visual = cv2.applyColorMap((heatmap_visual / heatmap.max() * 255).astype(np.uint8), cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(frame, 0.6, heatmap_visual, 0.4, 0)
    
    cv2.imshow('Heatmap Overlay', overlay)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Display final heatmap
plt.imshow(heatmap, cmap='hot', interpolation='nearest')
plt.title('Crowd Heatmap')
plt.colorbar()
plt.show()