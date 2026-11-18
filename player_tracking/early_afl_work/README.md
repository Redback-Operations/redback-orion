# Early AFL work

AFL player tracking prototypes and datasets from before the current pipeline. Nothing here is used by `player_service` or `pipeline`. It is kept so later work can build on it rather than start again.

| Folder | What it is |
|---|---|
| `Player_Tracking_BoTSORT/` | YOLOv11 tracker run with BoT-SORT (Drew, 2026 T1). Early version of the Forward-50 work now in `pipeline/forward50_analysis/` |
| `baselines/afl_yolov8_bytrack/` | Reproducible YOLOv8 + ByteTrack AFL baseline tracker |
| `football_detect/` | Roboflow-annotated AFL dataset and YOLO training scripts (Shafqat, 2026 T1) |
| `data_pipeline/` | Single data pipeline script (Shafqat, 2026 T1) |
| `Metric_Comparisons.ipynb` | Notebook comparing tracking metrics (2026 T1) |
