import json 
import os 
import time 
import psutil
import csv
from datetime import datetime

class ProcessingLogger:
    """
    Logs performance metrics for the Video Processing pipeline.
    """

    def __init__(self, output_dir="logs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.process = psutil.Process(os.getpid())

        self.start_time = None
        self.end_time = None

        self.frames_processed = 0
        self.frames_saved = 0

        self.cpu_samples = []
        self.memory_samples = []

    def start(self):
        self.process.cpu_percent(interval=None)
        self.start_time = time.perf_counter()

    def log_frame(self, saved=True):
        self.frames_processed += 1

        if saved:
            self.frames_saved += 1

        self.cpu_samples.append(self.process.cpu_percent(interval=None))
        self.memory_samples.append(self.process.memory_info().rss / (1024 * 1024))

    def stop(self):

        self.end_time = time.perf_counter()

        runtime = self.end_time - self.start_time

        fps = (
            self.frames_processed / runtime
            if runtime > 0
            else 0
        )

        results = {
            "timestamp": datetime.now().isoformat(),

            "runtime_seconds": round(runtime, 3),

            "processed_frames": self.frames_processed,

            "saved_frames": self.frames_saved,

            "processing_fps": round(fps, 2),

            "average_cpu_percent":
                round(sum(self.cpu_samples) / len(self.cpu_samples), 2)
                if self.cpu_samples else 0,

            "peak_cpu_percent":
                round(max(self.cpu_samples), 2)
                if self.cpu_samples else 0,

            "average_memory_mb":
                round(sum(self.memory_samples) / len(self.memory_samples), 2)
                if self.memory_samples else 0,

            "peak_memory_mb":
                round(max(self.memory_samples), 2)
                if self.memory_samples else 0
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = os.path.join(
            self.output_dir,
            f"processing_log_{timestamp}.json"
        )

        with open(filename, "w") as f:
            json.dump(results, f, indent=4)

        return results