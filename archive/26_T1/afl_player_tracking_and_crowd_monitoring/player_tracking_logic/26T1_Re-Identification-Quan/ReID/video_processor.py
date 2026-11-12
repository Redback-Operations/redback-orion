# processing/video_processor.py

import cv2

class VideoProcessor:

    def __init__(self, video_path, output_path="output.mp4"):
        self.cap = cv2.VideoCapture(video_path)

        width = int(self.cap.get(3))
        height = int(self.cap.get(4))
        fps = int(self.cap.get(5))

        self.writer = cv2.VideoWriter(
            output_path,
            cv2.VideoWriter_fourcc(*'mp4v'),
            fps,
            (width, height)
        )

    def read_video(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            yield frame

        self.cap.release()
        self.writer.release()