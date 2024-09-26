import cv2
import numpy as np
import dlib

def load_yolo_model(weights_path, config_path):
    net = cv2.dnn.readNet(weights_path, config_path)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    return net, output_layers

def detect_faces(img, net, output_layers, confidence_threshold=0.5):
    height, width, channels = img.shape

    # Prepare the image for the model
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    boxes = []
    confidences = []

    # Processing the output
    for out in outs:
        for detection in out:
            scores = detection[5:]
            confidence = max(scores)
            if confidence > confidence_threshold:  # Confidence threshold
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    faces = []
    selected_confidences = []
    for i in indexes.flatten():
        x, y, w, h = boxes[i]
        faces.append((x, y, w, h))
        selected_confidences.append(confidences[i])

    return faces, selected_confidences

def extract_face_characteristics(img, faces, shape_predictor, face_rec_model):
    characteristics = []
    for (x, y, w, h) in faces:
        face = img[y:y+h, x:x+w]
        rgb_face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)  # Convert to RGB
        
        # Predict face landmarks
        shape = shape_predictor(rgb_face, dlib.rectangle(0, 0, face.shape[1], face.shape[0]))

        # Get the face embedding
        face_descriptor = face_rec_model.compute_face_descriptor(rgb_face, shape)
        
        characteristics.append({
            'bbox': (x, y, w, h),
            'landmarks': [(p.x, p.y) for p in shape.parts()],
            'embedding': np.array(face_descriptor)
        })

    return characteristics