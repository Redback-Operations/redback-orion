## Matthew Lewis – Player Tracking

Location:
26_T1/afl_player_tracking_and_crowd_monitoring/player_tracking_logic/matthew_player_tracking/

Features:
- Player tracking using YOLOv8 + BoT-SORT
- Team classification using colour clustering (KMeans)
- Umpire detection using HSV colour thresholds
- Speed calculation (km/h)
- Acceleration calculation (m/s²)
- CSV export of player statistics

How to Run:

```bash
python player_tracking.py
```

Requirements:
- ultralytics
- opencv-python
- numpy
- scikit-learn