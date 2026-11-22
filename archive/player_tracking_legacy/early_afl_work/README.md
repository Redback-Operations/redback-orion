# Early AFL work

Player tracking prototypes from before the current pipeline. Archived in T3 2026: nothing in `player_tracking/` uses this code, and the 2026 audit found nothing here that the current pipeline doesn't already cover. See `player_tracking/docs/inventory.md`.

| Folder | What it is |
|---|---|
| `Player_Tracking_BoTSORT/` | YOLOv11 tracker run with BoT-SORT (Drew, 2026 T1). Early version of the Forward-50 work now in `player_tracking/experiments/forward50_analysis/` |
| `baselines/afl_yolov8_bytrack/` | YOLOv8 + ByteTrack AFL baseline tracker |
| `football_detect/` | Roboflow-annotated **soccer** dataset (Nations League broadcast frames) and YOLO training scripts for detecting a soccer ball. Not AFL footage, so it isn't suitable for AFL ball detection. |
| `data_pipeline/` | Single data pipeline script (Shafqat, 2026 T1) |
| `Metric_Comparisons.ipynb` | Notebook comparing tracking metrics (2026 T1) |
