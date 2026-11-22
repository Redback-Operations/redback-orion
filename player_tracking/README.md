# Player Tracking

Player Tracking follows AFL players through match footage. It finds every player and umpire in each frame, gives each one an ID that stays with them as they move, and turns those movements into data the Orion dashboard can show: who was where, how far and fast they ran, and events such as tackles.

It runs in three ways:

- **On its own from the command line**, for working on tracking and checking results
- **As `player_service`**, the web API the backend calls when someone uploads a video in the app
- **In the Orion Player Tracking Studio**, a desktop app for reviewing and correcting results

## How it works

```
match video
   │
   ▼
1. Detect and track      A YOLO model finds players and umpires in each frame.
   (detect_and_track.py) ByteTrack links them across frames so each keeps one ID.
   │                     → annotated video + tracks CSV (one row per player per frame)
   ▼
2. Analytics             Read the tracks: team colours, movement and speed,
   (player_service)      tackles, team formation.
   │
   ▼
results for the backend and dashboard
```

The default model is `player_ref_best.pt`. It recognises two classes, PLAYER and REF (umpire), and works on any match because it doesn't depend on team kits. Teams are worked out afterwards from jumper colour.

The tracks CSV has one row per detection:

| Column | Meaning |
|---|---|
| `frame` | Frame number in the source video (starting at 0) |
| `track_id` | The ID that follows one player across frames |
| `class` | `PLAYER` or `REF` |
| `confidence` | How sure the model is (0 to 1) |
| `x1, y1, x2, y2` | Bounding box corners in pixels |

## Folders

| Folder | What's in it |
|---|---|
| `analysis_pipeline/` | The pipeline itself. `detect_and_track.py` finds and follows players and writes the tracks CSV. |
| `player_service/` | The web API the backend calls (port 8001) |
| `orion_player_tracking_studio/` | Desktop app for reviewing and correcting tracking results |
| `player_tracking_logic/` | T1 code that `player_service` still runs for analytics, moving into `analysis_pipeline/` |
| `training/` | Datasets, labelling, model training, and the model and data download scripts |
| `evaluation/` | Tracking quality checks |
| `experiments/` | Ball tracking, Forward-50, jumper numbers: not in the pipeline yet |
| `docs/` | Setup details, code inventory and pipeline design |

Your local copies of `models/`, `data/`, `datasets/` and `outputs/` also live in this folder. Git ignores them.

## Getting started

You need Python 3.11 and [uv](https://docs.astral.sh/uv/). Run every command from `player_tracking/` unless a step says otherwise.

### 1. Install

```bash
cd player_tracking/player_service
uv venv .venv --python 3.11
source .venv/bin/activate          # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
cd ..
```

This one environment covers `player_service` and `analysis_pipeline/`. The first install is slow because it pulls in PyTorch.

### 2. Download the model

```bash
python training/download_models.py player_ref_best.pt
```

The weights come from the [`models-v1` release](https://github.com/Redback-Operations/redback-orion/releases/tag/models-v1) and are checked against a checksum. If the download fails, the message says why and what to do.

### 3. Get an AFL clip

Match footage is on the team Google Drive (about 16 GB, mostly full match videos):

```bash
uv pip install "gdown>=5"
python training/download_data.py data
```

Full matches are about two hours long, so cut a short clip to test with:

```bash
ffmpeg -ss 1200 -i data/videos/broadcast_essendon_hawthorn.mp4 -t 20 -c copy data/videos/test_clip_20s.mp4
```

Any AFL broadcast clip works if you already have one.

## Running it

### Track a video from the command line

```bash
python analysis_pipeline/detect_and_track.py data/videos/test_clip_20s.mp4
```

This writes two files to `outputs/`:

- `test_clip_20s_player_ref_best.mp4`: the video with a box, ID and class drawn on every player
- `test_clip_20s_player_ref_best.csv`: the tracks table described above

Useful options:

```bash
# Only the first 300 frames, for a quick test
python analysis_pipeline/detect_and_track.py data/videos/test_clip_20s.mp4 --max-frames 300

# The tracker settings tuned for broadcast footage (what player_service uses)
python analysis_pipeline/detect_and_track.py data/videos/test_clip_20s.mp4 \
  --tracker analysis_pipeline/configs/afl_broadcast_bytetrack.yaml

# A different model, or a lower confidence threshold
python analysis_pipeline/detect_and_track.py data/videos/test_clip_20s.mp4 \
  --model models/all_teams_best.pt --conf 0.3
```

Run `python analysis_pipeline/detect_and_track.py --help` for every option, including resuming a long run part-way through.

### Run the player service

```bash
cd player_service
source .venv/bin/activate
uvicorn main:app --port 8001
```

Open http://localhost:8001/docs, expand **POST /tracking**, click **Try it out**, choose your clip and click **Execute**. The result appears under **Server response** (the 200 and 422 listed below it are only documentation). The annotated video is saved in `player_service/outputs/tracks/`, and the response includes a `video_url` to download it.

The other endpoints:

| Endpoint | Input | What it returns |
|---|---|---|
| `POST /tracking` | video | Every player in every frame, plus the annotated video |
| `POST /path_trajectory` | video | Movement paths and metrics per player |
| `POST /jersey_color` | video + tracking JSON | Team for each player, from jumper colour |
| `POST /formation` | video + tracking JSON | Team shape overlay video |
| `POST /tackle` | tracking CSV | Tackle events with start and end times |

If you upload the same video twice, the second `/tracking` call reuses the first result and returns almost immediately.

### Run it inside the full app

Follow "Running the project" in the [root README](../README.md) to start the database, backend and frontend. Then set `USE_MOCK_PLAYER=false` in `backend/.env`, restart the backend, start `player_service` as above, and upload a clip at http://localhost:8080. The backend calls `/tracking` first, then the other four endpoints, and stores the results.

### Review results in the Studio

The Studio needs a desktop environment with Tk. Use the tools environment from [`docs/setup.md`](docs/setup.md), then:

```bash
uv pip install -r orion_player_tracking_studio/requirements.txt
cd orion_player_tracking_studio
python run_orion_tracking_studio.py
```

Open your clip with the tracks CSV from `outputs/`, choose **Load existing results**, and step through the flagged moments. You can correct teams and jumper numbers, join broken tracks of the same player, and export the corrected tracks. See the [Studio README](orion_player_tracking_studio/README.md) for the full workflow.

### Check tracking quality

```bash
python evaluation/analyze_tracking.py outputs/test_clip_20s_player_ref_best.csv \
  --fps 25 --output-prefix outputs/test_clip_quality
```

This lists short-lived tracks, sudden changes in player count and confidence drops, with timestamps to check in the annotated video. Add `--baseline <other.csv>` to compare two runs, for example two tracker settings.

### Train a model

```bash
python training/download_data.py datasets
python training/train.py player_ref --epochs 50
```

Training needs the tools environment and works best on a GPU. See [`docs/training.md`](docs/training.md) for the recipe and results.

## Testing

```bash
cd player_service && python -m pytest tests && cd ..
python -m pytest training/tests evaluation/tests experiments/forward50_analysis/tests
```

Install `pytest` into the environment first if it isn't there (`uv pip install pytest`).

## Something not working?

- **"Model not found"**: run `python training/download_models.py player_ref_best.pt`.
- **`/tracking` returns 503**: the service couldn't download the model. The response says why, usually no internet connection.
- **Google Drive download stops**: Drive blocks large files for about 24 hours after heavy use. Run the same command again later; finished files are skipped.
- **The annotated video won't play**: videos from `detect_and_track.py` are H.264 and play everywhere. Older outputs from before November 2026 may need converting with `ffmpeg -i in.mp4 -c:v libx264 -pix_fmt yuv420p out.mp4`.
- **Team labels are wrong**: the default model only knows PLAYER and REF. Team assignment from jumper colour can confuse similar kits; correct them in the Studio.

## More

- [`docs/setup.md`](docs/setup.md): full setup, including the separate tools environment and the data layout
- [`docs/target_pipeline.md`](docs/target_pipeline.md): how T1 and T2 are being merged into one pipeline, and how a video moves through it
- [`docs/inventory.md`](docs/inventory.md): what every folder contains and whether it runs
- [`docs/tools.md`](docs/tools.md): the labeller, quality checks and camera-motion tool in detail
