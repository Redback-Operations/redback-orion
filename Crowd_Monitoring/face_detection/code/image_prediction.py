# coding:utf-8
from ultralytics import YOLO
import cv2


def img_cvread(img_path):
    """Read the image and return the image array"""
    return cv2.imread(img_path)


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
    return cv_img, faces, locations


def adjust_parameters(width, height):
    """Adjust parameters based on image size"""
    base_width = 640
    scale = min(width / base_width, height / base_width)
    box_thickness = int(10 * scale)
    return box_thickness


if __name__ == '__main__':
    img_path    = ""  # Input  video file path
    output_path = ""  # Output video file path

    # Path to the face detection model
    face_model_path = 'face_detector.pt'

    # Load the face detection model
    face_model = YOLO(face_model_path, task='detect')

    cv_img = img_cvread(img_path)
    height, width = cv_img.shape[:2]

    # Adjust parameters
    box_thickness = adjust_parameters(width, height)

    # Perform face detection
    face_cvimg, faces, locations = face_detect(cv_img, face_model)

    if faces:
        for i in range(len(faces)):
            left, top, right, bottom = locations[i]
            # Draw rectangle around the detected face
            face_cvimg = cv2.rectangle(face_cvimg, (left, top), (right, bottom), (50, 50, 250), box_thickness)

    # Save the predicted image
    cv2.imwrite(output_path, face_cvimg)

    # Display the predicted image
    cv2.imshow('yolov8_detections', face_cvimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
