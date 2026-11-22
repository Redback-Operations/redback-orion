# %%
## Define tracker and evaluator intereface
from abc import ABC, abstractmethod

class BaseTracker(ABC):
    @abstractmethod
    def run(self, video_path, model_path, output_path):
        pass

# %% [markdown]
# ## Tracker 

# %%
from ultralytics import YOLO
import cv2

class UltralyticsTracker:
    def __init__(self, tracker_type):
        self.tracker_type = tracker_type    #bytetrack or botsort

    def run(self, video_path, model_path, output_path):
        model = YOLO(model_path)

        cap = cv2.VideoCapture(video_path)

        width = int(cap.get(3))
        height = int(cap.get(4))
        fps = cap.get(cv2.CAP_PROP_FPS)

        out = cv2.VideoWriter(
            output_path,
            cv2.VideoWriter_fourcc(*'mp4v'),
            fps,
            (width, height)
        )

        results = model.track(
            source=video_path,
            tracker=f"{self.tracker_type}.yaml",
            stream=True,
            persist=True,
            verbose=False
        )

        for result in results:  # generator (NO memory explosion)
            frame = result.orig_img.copy()

            if result.boxes is not None and result.boxes.xyxy is not None:

                boxes = result.boxes.xyxy.cpu().numpy()

                #IDs may be None
                ids = result.boxes.id

                if ids is not None:
                    ids = ids.cpu().numpy()
                else:
                    ids = [None] * len(boxes)

                for box, track_id in zip(boxes, ids):

                    x1, y1, x2, y2 = map(int, box)

                    if track_id is None:
                        label = "NoID"
                    else:
                        track_id = int(track_id)
                        label = f"ID {track_id}"

                    cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                    cv2.putText(frame, label, (x1,y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

            out.write(frame)

        cap.release()
        out.release()

        return output_path

# %%
# ----- deep sort
from deep_sort_realtime.deepsort_tracker import DeepSort

class DeepSortTracker(BaseTracker):
    def run(self, video_path, model_path, output_path):
        model = YOLO(model_path)
        tracker = DeepSort(max_age=30)

        cap = cv2.VideoCapture(video_path)

        width = int(cap.get(3))
        height = int(cap.get(4))
        fps = cap.get(cv2.CAP_PROP_FPS)

        out = cv2.VideoWriter(
            output_path,
            cv2.VideoWriter_fourcc(*'mp4v'),
            fps,
            (width, height)
        )

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)[0]

            detections = []
            for box in results.boxes.data.cpu().numpy():
                x1, y1, x2, y2, conf, cls = box
                detections.append(([x1, y1, x2-x1, y2-y1], conf, cls))

            tracks = tracker.update_tracks(detections, frame=frame)

            for t in tracks:
                if not t.is_confirmed():
                    continue

                l, t_, r, b = map(int, t.to_ltrb())
                track_id = t.track_id

                cv2.rectangle(frame, (l,t_), (r,b), (255,0,0), 2)
                cv2.putText(frame, f"ID {track_id}", (l,t_-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)

            out.write(frame)

        cap.release()
        out.release()

        return output_path

# %% [markdown]
# ## Evaluator

# %%
import time

class TrackerEvaluator:
    def __init__(self):
        self.results = {}

    def evaluate(self, name, tracker, video_path, model_path):
        start = time.time()

        output_path = f"{name}_output.mp4"
        tracker.run(video_path, model_path, output_path)

        end = time.time()

        self.results[name] = {
            "output_video": output_path,
            "runtime_sec": round(end - start, 2)
        }

    def report(self):
        print("\n=== TRACKING COMPARISON REPORT ===\n")
        for k, v in self.results.items():
            print(f"{k}:")
            print(f"  Output: {v['output_video']}")
            print(f"  Runtime: {v['runtime_sec']} sec\n")

# %% [markdown]
# ## Tracking Video Processing

# %%
import os
def main():

    video_path = os.path.join("..","afl_video.mp4")
    model_path = os.path.join("..","best.pt")


    evaluator = TrackerEvaluator()

    trackers = {
        #"DeepSORT": DeepSortTracker(),
        "BoT-SORT": UltralyticsTracker("botsort"),
        "ByteTrack": UltralyticsTracker("bytetrack"),
    }

    for name, tracker in trackers.items():
        print(f"Running {name}...")
        evaluator.evaluate(name, tracker, video_path, model_path)

    evaluator.report()


if __name__ == "__main__":
    main()


