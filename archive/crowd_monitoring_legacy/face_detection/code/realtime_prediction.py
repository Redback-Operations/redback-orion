# coding:utf-8
from ultralytics import YOLO
import cv2


def face_detect(cv_img, face_model):
    """Perform face detection and return detected face images and their locations"""
    results = face_model(cv_img)
    faces = []
    locations = []
    for result in results:
        for bbox in result.boxes:
            x1, y1, x2, y2 = map(int, bbox.xyxy[0].cpu().numpy())
            face = cv_img[y1:y2, x1:x2]
            faces.append(face)
            locations.append((x1, y1, x2, y2))
    return cv_img, locations


def adjust_parameters(width, height):
    """Adjust parameters based on image size"""
    base_width = 640
    scale = min(width / base_width, height / base_width)
    box_thickness = int(10 * scale)
    return box_thickness


if __name__ == '__main__':
    # Path to the face detection model
    face_model_path = 'face_detector.pt'

    # Load the face detection model
    face_model = YOLO(face_model_path, task='detect')

    # Open the camera, 0 indicates the default camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame.")
            break

        height, width = frame.shape[:2]

        # Adjust parameters
        box_thickness = adjust_parameters(width, height)

        # Perform face detection
        face_cvimg, locations = face_detect(frame, face_model)

        if locations:
            for (left, top, right, bottom) in locations:
                # Draw rectangle around detected faces
                face_cvimg = cv2.rectangle(face_cvimg, (left, top), (right, bottom), (50, 50, 250), box_thickness)

        # Display the frame with detection results
        cv2.imshow('Face Detection System', face_cvimg)

        # Exit the loop when 'q' key is pressed
        if cv2.waitKey(1) == ord('q'):
            break

    # Release the camera resource
    cap.release()
    # Close all OpenCV windows
    cv2.destroyAllWindows()
