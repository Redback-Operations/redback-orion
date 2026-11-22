# Player tracking pipeline

How the T1 and T2 player tracking code became one pipeline (PR #161, November 2026), how a teammate runs it, and what's still open. The audit behind it is in `inventory.md`.

## The idea

Detect and track once, write one tracks table, and have every later stage read that table. No stage runs the detection model a second time.

```
match video
   │
   ▼
1. detect_and_track      YOLO + ByteTrack (player_ref_best.pt, broadcast tracker config)
   │  → tracks.csv + annotated video
   ▼
2. analytics             each reads the tracks
   ├─ identify_players     team from jumper colour
   ├─ movement_metrics     speed and distance per player, trajectory video
   │                       (field calibration when reference points are given)
   ├─ tackle_detection     tackle events
   ├─ workload_heatmaps    distance, high-speed running, sprints, heatmaps
   └─ formation_analysis   team shape overlay
   ▼
results.json (command line) or the five endpoint responses (player_service)
```

The tracks table is the CSV `detect_and_track.py` writes: `frame, track_id, class, confidence, x1, y1, x2, y2`. `tracking_json.py` converts it into the two shapes the T1 stages read: the JSON `/tracking` returns, and a per-player table with centre points and timestamps.

## Folder layout

```
player_tracking/
├── analysis_pipeline/
│   ├── run_pipeline.py          runs every stage on one video
│   ├── detect_and_track.py      stage 1: find and follow players
│   ├── tracking_json.py         converts the tracks CSV for the T1 stages
│   ├── identify_players/        team from jumper colour (was JerseyColorDetection)
│   ├── movement_metrics/        speed, distance, calibration (was Tracking_Ethan)
│   ├── tackle_detection.py      tackle events (the logic /tackle always ran)
│   ├── workload_heatmaps/       workload and heatmaps
│   ├── formation_analysis/      team shape (was Formation_Visualization)
│   ├── configs/
│   └── tests/
├── player_service/              The web API the backend calls (name, port, endpoints and responses unchanged)
├── orion_player_tracking_studio/  Desktop review app
├── training/  evaluation/  experiments/
├── models/                      Weights from the models-v1 release (git-ignored)
└── docs/
```

The T1 stages stayed as folders, not single files, because each is a small package with its own modules. Splitting them up would have meant rewriting working code. Everything moved with `git mv`, so history is kept. The rest of `player_tracking_logic/` is in `archive/player_tracking_legacy/player_tracking_logic/`.

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

Stage 1 runs the model once and every analytics stage reads its tracks. Everything goes to `outputs/test_clip_20s/`: the tracks, annotated videos, team clusters, per-player movement metrics, tackles, workload, heatmaps, the formation video and a `results.json` summary. If one analytics stage fails, the others still run and `results.json` records the error. On a 20-second clip the whole run takes about 40 seconds on a laptop CPU.

### Way 2: the service

```bash
cd player_service
uvicorn main:app --port 8001
```

Open http://localhost:8001/docs and try `POST /tracking`. The service runs stage 1, saves the tracks under the uploaded file's hash, and returns the JSON shape the backend has always received.

Endpoints that need tracks get them through `tracks.get_tracks()`. If tracking already ran on that file, the saved tracks are reused. If not, tracking runs first, so calling an endpoint on its own is slower but never fails for lack of tracks. `/path_trajectory` works this way: after `/tracking` it takes about 4 seconds instead of 17, and its player IDs match `/tracking`.

### Way 3: the whole app

Follow the root README: start the database, backend and frontend, set `USE_MOCK_PLAYER=false` in `backend/.env`, start `player_service`, and upload a clip at http://localhost:8080.

```
Browser upload → Backend /upload → player_service /tracking         (detects once, saves tracks)
                                 → /jersey_color, /formation, /tackle (read the tracks the backend sends)
                                 → /path_trajectory                   (reuses the saved tracks)
                                 → Backend stores results in Postgres → Frontend shows them
```

### Reviewing results

```bash
cd orion_player_tracking_studio
python run_orion_tracking_studio.py
```

Open the clip with its tracks CSV, step through flagged moments, fix teams and jumper numbers, merge fragments of the same player and export the corrected tracks.

## What changed, measured on a 20-second AFL clip

| | Before | After |
|---|---|---|
| Model | T1 CAR/GCS/REF, one match | `player_ref_best.pt`, any match |
| Detection passes per upload | 2 (`/tracking` and `/path_trajectory`) | 1 |
| `/path_trajectory` after `/tracking` | 16.9 s | 4.0 s |
| Player tracks in `/path_trajectory` | 55 (own matcher, IDs differ from `/tracking`) | 28 (ByteTrack, same IDs as `/tracking`) |
| `/jersey_color`, `/formation`, `/tackle` | | Same output as before |

The tracker comparison the plan called for came out clearly: on the same clip, Tracking_Ethan's matcher split the players into 55 tracks and ByteTrack into 28, so ByteTrack is kept and the matcher is removed.

## Still open

- **Team classification test.** JerseyColorDetection stays as the team stage. Comparing it with the Studio's team suggestion needs clips with known teams to score against. Nobody has labelled any yet.
- **Studio logic in the pipeline.** The Studio's jumper OCR and identity merging aren't in `analysis_pipeline/` yet. Nothing in the service or backend uses them, and moving them would make the desktop app depend on the pipeline folder. Do it when an endpoint or the dashboard needs jumper numbers.
- **Acceleration per player.** Speed and distance are reported. Drew's T1 acceleration code is archived and not yet carried over.
- **One endpoint, with Backend.** A single `POST /analyse` returning `results.json` would replace five calls, once the backend contract includes player metrics.

## Known limits

- Real-world speeds are approximate on broadcast footage (`metric_mode: pixel_estimate`): camera movement and zoom change the pixel scale, and calibration needs field reference points on a stable shot.
- Team labels from a PLAYER/REF model rely on jumper colour, so similar kits (for example Swans and Bulldogs) need correcting in the Studio.
- Two uploads of the same new video at the same moment both run tracking. The results are identical, so this only wastes time.
