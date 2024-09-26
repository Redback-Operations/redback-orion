import cv2
import json
from models import detect_faces, extract_face_characteristics

def process_video(video_path, net, output_layers, shape_predictor, face_rec_model):
    cap = cv2.VideoCapture(video_path)
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % (frame_rate // 3) == 0:  # Process 3 frames per second
            faces, confidences = detect_faces(frame, net, output_layers, confidence_threshold=0.5)
            
            if faces:  # Skip processing if no faces are detected
                characteristics = extract_face_characteristics(frame, faces, shape_predictor, face_rec_model)

                frame_data = {
                    'frame_id': frame_count,
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

                # Optionally print the JSON result of the current frame
                print(json.dumps(frame_data, indent=4))

        frame_count += 1

    cap.release()