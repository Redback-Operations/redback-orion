# Target pipeline

How the T1 and T2 player tracking code becomes one pipeline, and how a teammate will run it. The audit behind this is in `inventory.md`.

## The idea

Detect and track once, write one tracks table, and have every later stage read that table. No stage runs the detection model a second time.

```
match video
   │
   ▼
1. detect_and_track     YOLO + ByteTrack (player_ref_best.pt, broadcast tracker config)
   │  → tracks.csv + annotated video
   ▼
2. identify_players     team, jumper number, joining broken tracks into one player
   │  → adds team, jumper, player_uid
   ▼
3. field_calibration    screen pixels → field metres (approximate ratio when uncalibrated)
   │  → adds field_x, field_y
   ▼
4. analytics            each reads tracks.csv
   ├─ movement_metrics    speed, acceleration, distance
   ├─ workload_heatmaps   heatmaps, sprints
   ├─ tackle_detection    contest events
   └─ formation_analysis  team shape
   ▼
5. result               one JSON: summary, per-player metrics, events, file links
```

The tracks table is the T2 CSV that `detect_and_track.py` and the Studio already use, extended column by column:

| Columns | Added by |
|---|---|
| `frame, track_id, class, confidence, x1, y1, x2, y2` | stage 1 (exists now) |
| `team, jumper, player_uid` | stage 2 |
| `field_x, field_y` | stage 3 |

## Folder layout

```
player_tracking/
├── analysis_pipeline/            One file per stage, in the order they run
│   ├── detect_and_track.py         1 find and follow players → tracks.csv
│   ├── identify_players.py         2 team, jumper, identity   ← Studio core.py / vision.py
│   ├── field_calibration.py        3 pixels → metres          ← Tracking_Ethan calibration
│   ├── movement_metrics.py         4 speed / accel / distance ← Tracking_Ethan metrics + Drew's fields
│   ├── workload_heatmaps.py          heatmaps, sprints        ← heatmaps_workload
│   ├── tackle_detection.py           contest events           ← tackle_detection_shafqat_ullah
│   ├── formation_analysis.py         team shape               ← Formation_Visualization
│   ├── run_pipeline.py             runs the stages and writes the result
│   └── configs/
├── player_service/               The web API the backend calls (name, port and endpoints unchanged)
├── orion_player_tracking_studio/ Desktop review app; imports identify_players.py
├── training/  evaluation/  experiments/
├── models/                       Weights from the models-v1 release (git-ignored)
└── docs/
```

`player_tracking_logic/` disappears once its useful code has moved into `analysis_pipeline/`. Moves use `git mv`, so file history is kept.

## How a teammate runs it

### Once

```bash
cd redback-orion/player_tracking/player_service
uv venv .venv --python 3.11 && source .venv/bin/activate
uv pip install -r requirements.txt
cd ..
python training/download_models.py player_ref_best.pt
```

They also need an AFL clip. See `setup.md` for downloading match footage and cutting a short test clip.

### Way 1: command line

```bash
python analysis_pipeline/run_pipeline.py data/videos/test_clip_20s.mp4
```

Stage 1 runs the model once. Every later stage reads the tracks table, so they're fast. The output folder holds `tracks.csv`, the annotated video, `results.json` and per-player heatmaps. Until `run_pipeline.py` exists, stage 1 runs on its own with `python analysis_pipeline/detect_and_track.py`.

### Way 2: the service

```bash
cd player_service
uvicorn main:app --port 8001
```

Open http://localhost:8001/docs and try `POST /tracking`. The service runs stage 1, saves the tracks under the uploaded file's hash, and returns the JSON shape the backend has always received.

Any endpoint that needs tracks gets them through `tracks.get_tracks()`. If tracking already ran on that file, the saved tracks are reused. If not, tracking runs first. Calling an endpoint on its own is slower, but it never fails for lack of tracks.

### Way 3: the whole app

Follow the root README: start the database, backend and frontend, set `USE_MOCK_PLAYER=false` in `backend/.env`, start `player_service`, and upload a clip at http://localhost:8080.

```
Browser upload → Backend /upload → player_service /tracking         (tracks once)
                                 → /jersey_color, /formation,        (reuse the tracks)
                                   /tackle, /path_trajectory
                                 → Backend stores results in Postgres → Frontend shows them
```

### Reviewing results

```bash
cd orion_player_tracking_studio
python run_orion_tracking_studio.py
```

Open the clip with its tracks CSV, step through flagged moments, fix teams and jumper numbers, merge fragments of the same player and export the corrected tracks.

## Plan

### PR 1: restructure and switch to the T2 model (this PR)

- Archive `early_afl_work/`, `generic_sports_cv/` and the unused T1 code
- Split `pipeline/` into `analysis_pipeline/`, `training/`, `evaluation/`, `experiments/` and `docs/`
- `training/download_models.py` fetches weights from the `models-v1` GitHub release and checks their SHA-256
- `training/download_data.py` explains Drive failures and resumes
- `/tracking` runs `detect_and_track.py` with `player_ref_best.pt` and the broadcast tracker config, saves tracks by file hash, and keeps its response shape
- This inventory and design

### PR 2: one tracking pass, all analytics in the pipeline

- Add the remaining stage files from T1 and the Studio. The Studio imports `identify_players.py`.
- All five endpoints keep their names, inputs and response shapes, but read the saved tracks through `get_tracks()`, falling back to running tracking when nothing is saved
- `/path_trajectory` stops running its own detection, so every upload runs the model once
- `run_pipeline.py` for the command line
- Archive the rest of `player_tracking_logic/`

### Two choices to settle by testing in PR 2

1. Team classification: run every candidate on the same clips, count correct team labels and keep the best.
2. Tracker: compare `detect_and_track.py` with Tracking_Ethan's tracker using `evaluation/analyze_tracking.py` (fewer short tracks and ID changes is better). Keep T2 unless Tracking_Ethan's is clearly better.

### Later, with Backend

A single `POST /analyse` that returns the whole result in one call, once the backend contract includes player metrics. It needs backend changes, so it isn't part of PR 1 or PR 2.

## Known limits

- Real-world speeds are approximate on broadcast footage: camera movement and zoom change the pixel scale, and calibration needs field reference points on a stable shot.
- Team labels from a PLAYER/REF model rely on jumper colour, so similar kits (for example Swans and Bulldogs) need correcting in the Studio.
- Two uploads of the same new video at the same moment both run tracking. The results are identical, so this only wastes time.
