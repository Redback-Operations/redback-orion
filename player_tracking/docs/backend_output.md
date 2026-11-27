# Player tracking output for the backend (`POST /analyse`)

Draft response format for a new `player_service` endpoint, `POST /analyse`, plus a timing check. For Henry to fold into `backend/API_CONTRACT.md` (v2) and for Luke and the frontend to review.

Status: **draft for review**. Nothing here is built yet. The five existing endpoints (`/tracking`, `/path_trajectory`, `/jersey_color`, `/tackle`, `/formation`) stay unchanged until the backend switches over.

## Why one endpoint

Today `backend/app/routes/upload.py` (`process_video`) calls five player endpoints and stores the answers as `player_result`. `analysis_pipeline/run_pipeline.py` already produces all of that in one run, tracking the video once. `POST /analyse` runs it and returns one response, so the backend makes one call instead of five, and the frontend gets per-player metrics it can't get today.

## Request

```
POST /analyse
Content-Type: multipart/form-data
video: <file>          .mp4, .avi or .mov
```

If the same file was tracked before (by `/tracking` or `/analyse`), the saved tracks are reused (`player_service/tracks.py`, keyed by the file's SHA-256), so tracking never runs twice for one video.

## Response `200`

Values are real output from the 5-minute timing clip (`workload_clip.mp4`, see Timing); lists are cut to one item. See "What the sample shows" below before trusting the numbers.

```json
{
  "status": "success",
  "video_id": "9f2c…e41a",
  "metric_mode": "pixel_estimate",
  "calibration_available": false,
  "processing_seconds": 617.7,

  "tracking": {
    "status": "success",
    "video_info": {"duration": 302.08, "fps": 25, "total_frames": 7552, "resolution": [1920, 1080]},
    "tracking_results": [
      {
        "frame_number": 3092,
        "timestamp": 123.64,
        "players": [
          {
            "player_id": 2317, "team_id": 0, "team_name": "PLAYER",
            "bbox": {"x1": 1521, "y1": 509, "x2": 1560, "y2": 593},
            "center": {"x": 1540, "y": 551},
            "confidence": 0.61, "width": 38, "height": 83
          }
        ]
      }
    ],
    "video_url": "/outputs/9f2c…e41a/tracks.mp4"
  },

  "players": [
    {
      "track_id": 2317,
      "role": "PLAYER",
      "team": "Cluster_1",
      "player_uid": null,
      "jumper_number": null,
      "first_seen_s": 123.64,
      "last_seen_s": 142.56,
      "distance_m": 133.6,
      "avg_speed_kmh": 25.4,
      "max_speed_kmh": 39.7,
      "max_accel_mps2": null,
      "workload_score": 50.0,
      "fatigue_risk": "Moderate",
      "zone": null,
      "reviewed": false
    }
  ],

  "events": {
    "tackles": [
      {
        "event_id": 2, "event_type": "multi_player_tackle",
        "start_frame": 3776, "end_frame": 3795,
        "start_time_s": 151.0, "end_time_s": 151.76, "duration_frames": 20,
        "players_involved": 32, "cluster_score": 41.65, "confidence": 1.0,
        "bounding_box": {"x_min": 31, "y_min": 451, "x_max": 1124, "y_max": 785}
      }
    ]
  },

  "files": {
    "tracks_video": "/outputs/9f2c…e41a/tracks.mp4",
    "tracks_csv": "/outputs/9f2c…e41a/tracks.csv",
    "teams_video": "/outputs/9f2c…e41a/teams/workload_clip_clustered.mp4",
    "movement_video": "/outputs/9f2c…e41a/movement/trajectory.mp4",
    "metrics_csv": "/outputs/9f2c…e41a/movement/player_metrics.csv",
    "formation_video": "/outputs/9f2c…e41a/formation.mp4",
    "heatmaps": "/outputs/9f2c…e41a/heatmaps/"
  },

  "errors": {}
}
```


### What the sample shows

The format is the point of this draft; the numbers show where the pipeline is today, and the frontend should not present them as reliable yet.

- **Tracks are short.** The longest player track in 5 minutes is 19 seconds, and there are 945 track IDs for 36 players and a handful of umpires on the ground. Players get a new ID every time they leave the frame or the camera cuts. Per-player totals only become meaningful once tracks are joined into players (`player_uid`, Yash, Sprint 3).
- **Speeds are too high.** 25 km/h average and 40 km/h top speed over 19 seconds is not realistic (AFL top speeds are around 30 to 35 km/h). The pixel estimate doesn't allow for the camera panning and zooming. This is what `metric_mode: "pixel_estimate"` warns about, and it's being worked on (workload fixes, field calibration).
- **The tackle event is a false positive.** 32 players "involved" means a crowded wide shot, not a tackle. The rule thresholds have never been measured against labelled tackles (Tyson's ML task).

### Fields

| Field | Meaning |
|---|---|
| `status` | `success` when every stage ran; `partial` when at least one stage failed (see `errors`). Tracking failing is an HTTP error, not `partial`. |
| `video_id` | SHA-256 of the uploaded file. The same video always gets the same id. |
| `metric_mode` | `pixel_estimate` today: distances and speeds use a fixed metres-per-pixel guess, not real field calibration. The dashboard should label them as estimates. `calibrated` once field calibration lands. |
| `calibration_available` | `true` only when distances are in calibrated metres. |
| `processing_seconds` | How long the request took on the server. |
| `tracking` | **Exactly the shape `/tracking` returns today**, so `analytics.py` and anything reading `player_result.tracking` keep working without changes. |
| `players[]` | One row per track. A track is one continuous follow of one person; the same real player can get several tracks if they leave the screen. |
| `players[].track_id` | Matches `player_id` in `tracking.tracking_results`. |
| `players[].role` | `PLAYER` or `REF`. |
| `players[].team` | Team group from jumper colour (`identify_players`). A cluster label, not a club name, until team classification is finalised (Nonye's comparison, Sprint 3). |
| `players[].player_uid`, `jumper_number`, `reviewed` | `null` / `false` for now. Filled by the jumper-number and identity stages (Yash, Sprint 2–3): `player_uid` joins several tracks of the same player, `reviewed` is true once a person has confirmed it in the Studio. Kept separate from `team`, as the T2 handover asked. |
| `players[].distance_m`, `avg_speed_kmh`, `max_speed_kmh` | From `movement_metrics`. Estimates, see `metric_mode`. |
| `players[].max_accel_mps2` | `null` until per-player acceleration is built (Backlog task). |
| `players[].workload_score`, `fatigue_risk` | From `workload_heatmaps`. `fatigue_risk` is `Low`, `Moderate` or `High`. The score is being reworked this sprint (Tyson) to be absolute rather than relative to other players in the clip; field names stay the same. |
| `players[].zone` | `null` for now. Field zone per player needs field calibration. |
| `events.tackles[]` | Tackle events from the rule-based detector (`tackle_detection.py`), the same objects `/tackle` returns as `events`. Times are seconds from the start of the video. Empty list when none are found. The detector's thresholds haven't been measured yet (Tyson's ML task), so treat these as candidates. |
| `files` | Output files, as `/outputs/...` paths on the player service. `result_formatter.py` turns known keys (`video_url`, `csv_url`, `metrics_csv_url`) into full URLs today; it needs to do the same for the values in `files`. |
| `errors` | Stage name → error message for any stage that failed, e.g. `{"workload": "RuntimeError: ..."}`. Empty when everything ran. |

Every field that isn't built yet is present with `null`, so the frontend can code against the final shape now.

### Errors

| Code | When |
|---|---|
| `400` | Not a video file (proposed; same check the backend's `/upload` already does). |
| `500` | Tracking itself failed. Body: `{"detail": "..."}`, the same as the current endpoints. |

## Timing

Measured 2026-11-27 on `run_pipeline.py` (what `/analyse` will run), on a 5-minute clip of live play (Essendon vs Hawthorn, 1920x1080, 25 fps, 7,502 frames). Machine: Apple M4 Pro laptop, 48 GB RAM, using the Mac GPU (MPS). No stage errors.

| Stage | Time | Notes |
|---|---|---|
| Detect and track | ~3 min 53 s | YOLO + ByteTrack, 945 track IDs |
| Teams (jumper colour) | ~1 min 3 s | |
| Movement metrics | ~1 min 3 s | |
| Tackles | ~1 s | 1 candidate event |
| Workload + heatmaps | ~3 min 30 s | Almost all of it is drawing one heatmap per track (945 PNGs) |
| Formation video | ~46 s | |
| **Total** | **10 min 18 s** | about **2x the length of the clip** |

Stage times are from the output files' timestamps, so they're approximate; the total is measured.

What it means:

- **A 5-minute clip fits in one request, just.** 10 minutes is under the backend's longest current timeout (1000 s for `/path_trajectory` and `/formation`), with little margin. A slower machine (no GPU) would go over.
- **A full match does not.** At about 2x real time, a full broadcast (roughly 2.5 hours of video) would take around 5 hours. Detection alone would be about 2 hours, far past the 600 s `/tracking` allows today.
- **Recommendation:** make `/analyse` a background job from the start: `POST /analyse` saves the video and returns a `job_id` straight away; `GET /analyse/{job_id}` returns `{"status": "processing", "progress": 40}` until it's done, then the response above. The backend already works this way with its own jobs (`/status/{job_id}`), so it would poll the player service the same way instead of holding one HTTP request open.
- **Response size:** `tracking.json` for 5 minutes is 11 MB (7,502 frames, 945 tracks). A full match would be roughly 30 times that, which is a reason to consider leaving `tracking_results` out of the response.
- **Easy speed-up:** heatmaps for very short tracks (a few seconds on screen) are a third of the time and aren't useful. Skipping tracks shorter than, say, 5 seconds would cut that stage sharply. Separate change; not needed for the format.

## Things the backend should know

- **Two dashboard numbers are always 0 today.** `backend/app/routes/analytics.py` reads `player_result.tackle.tackles`, but `/tackle` returns `events`; and it reads `player_result.formation.formations`, but `/formation` returns only `video_url`. So tackle and formation counts show 0 whatever the video. With `/analyse`, tackles move to `events.tackles`; `analytics.py` needs that one-line change when the backend switches.
- **Distances differ slightly between two modules.** `movement_metrics` and `workload_heatmaps` each convert pixels to metres their own way. `/analyse` takes distance and speed from `movement_metrics` only, and workload score and fatigue from `workload_heatmaps`, so each number has one source.
- **No change is needed in the backend until it chooses to switch.** The existing endpoints keep working.
