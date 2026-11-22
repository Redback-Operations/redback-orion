import cv2
from ultralytics import YOLO

MODEL_PATH = 'yolo_merged_best.pt'
VIDEOS = ['test_1.mp4', 'test_2.mp4']

model = YOLO(MODEL_PATH)
class_names = model.names

for video_path in VIDEOS:
    out_path = video_path.replace('.mp4', '_tracked.mp4')
    print(f'processing {video_path} -> {out_path}')

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

    results = model.track(source=video_path, tracker='bytetrack.yaml', persist=True, stream=True, verbose=False)

    n_frames = 0
    for r in results:
        frame = r.plot()

        counts = {name: 0 for name in class_names.values()}
        if r.boxes is not None:
            for cls_id in r.boxes.cls.tolist():
                counts[class_names[int(cls_id)]] += 1

        text = '  '.join(f'{name}:{count}' for name, count in counts.items())
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        writer.write(frame)
        n_frames += 1

    writer.release()
    print(f'done, {n_frames} frames written to {out_path}')
