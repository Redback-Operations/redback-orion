import cv2
from pathlib import Path

VIDEO = "videos/side.mp4"
FRAMES = [0, 10, 20, 30, 40]

Path("truth_frames").mkdir(exist_ok=True)
cap = cv2.VideoCapture(VIDEO)

for i in FRAMES:
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ok, frame = cap.read()
    if ok:
        cv2.imwrite(f"truth_frames/frame_{i:04d}.jpg", frame)
        print(f"written frame {i}")

cap.release()