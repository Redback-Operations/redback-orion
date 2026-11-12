import cv2 #import the OpenCV library for video processing


def open_video(video_path):
    cap = cv2.VideoCapture(video_path) #create a VideoCapture object to read the video frame by frame

    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) #get the frames per second of the video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) #get the width of the video frames
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) #get the height of the video frames

    return cap, fps, width, height


def create_video_writer(output_path, fps, width, height):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v") #specify the codec for the output video (mp4v for MP4 format)
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height)) #create a VideoWriter object to write the output video

    if not writer.isOpened():
        raise ValueError(f"Could not create video writer: {output_path}")

    return writer