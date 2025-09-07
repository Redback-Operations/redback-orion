# coding:utf-8
from ultralytics import YOLO
import cv2
import os
from moviepy.editor import VideoFileClip, AudioFileClip


def validate_file_path(file_path, base_dir="."):
    """
    Validate if a file path is within a specific base directory.
    Prevents directory traversal attacks.
    """
    abs_path = os.path.abspath(file_path)
    base_dir = os.path.abspath(base_dir)

    if not abs_path.startswith(base_dir):
        raise ValueError(f"Invalid file path: {file_path}")

    return abs_path


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


def process_frame(frame, face_model):
    """Process video frame for face detection"""
    face_cvimg, locations = face_detect(frame, face_model)

    if locations:
        for (left, top, right, bottom) in locations:
            # Draw rectangle around detected faces
            face_cvimg = cv2.rectangle(face_cvimg, (left, top), (right, bottom), (50, 50, 250), 2)

    return face_cvimg


if __name__ == '__main__':
    base_dir = "."  # Define a base directory to validate file paths

    video_path = ""     # Input video file path
    output_path = ""    # Output video file path

    # Validate file paths
    try:
        video_path = validate_file_path(video_path, base_dir)
        output_path = validate_file_path(output_path, base_dir)
    except ValueError as e:
        print(e)
        exit()

    # Path to the face detection model
    face_model_path = 'face_detector.pt'

    # Load the face detection model
    face_model = YOLO(face_model_path)

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file: {video_path}")
        exit()

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Open video writer
    out = cv2.VideoWriter('temp_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process each frame
        processed_frame = process_frame(frame, face_model)

        # Display the result
        cv2.imshow('Face Detection', processed_frame)

        # Write the processed frame
        out.write(processed_frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # Combine processed video with original audio
    video_clip = VideoFileClip("temp_video.mp4")
    audio_clip = AudioFileClip(video_path)
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_path, codec='libx264')
