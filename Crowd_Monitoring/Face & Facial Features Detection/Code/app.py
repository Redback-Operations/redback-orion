from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from models import load_yolo_model, detect_faces, extract_face_characteristics
import config
import dlib

app = FastAPI()

# Load the YOLO and Dlib models
net, output_layers = load_yolo_model(config.weights_path, config.config_path)
shape_predictor = dlib.shape_predictor(config.shape_predictor_path)
face_rec_model = dlib.face_recognition_model_v1(config.face_rec_model_path)

@app.post("/process_frame/")
async def process_frame(file: UploadFile = File(...)):
    # Read the uploaded file
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    
    # Decode the image using OpenCV
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Detect faces in the image
    faces, confidences = detect_faces(img, net, output_layers, confidence_threshold=0.5)

    if faces:  # If faces are detected, extract face characteristics
        characteristics = extract_face_characteristics(img, faces, shape_predictor, face_rec_model)

        frame_data = {
            'face_count': len(faces),
            'faces': []
        }

        for idx, face_data in enumerate(characteristics):
            face_info = {
                'face_id': idx,
                'bbox': face_data['bbox'],
                'confidence': confidences[idx],  # Add confidence score
                'landmarks': face_data['landmarks'],
                'embedding': face_data['embedding'].tolist()  # Convert to list for JSON serialization
            }
            frame_data['faces'].append(face_info)

        # Return the face information as JSON
        return JSONResponse(content=frame_data)

    return {"message": "No faces detected"}
