# Player Tracking

Follows AFL players through match footage and turns their movement into analytics for the Orion dashboard.

| Folder | What's in it |
|---|---|
| `analysis_pipeline/` | Runs a match video through tracking: `detect_and_track.py` finds and follows players and writes a tracks CSV |
| `player_service/` | The web API the backend calls (port 8001) |
| `orion_player_tracking_studio/` | Desktop app for reviewing and correcting tracking results |
| `player_tracking_logic/` | T1 code that `player_service` still runs, moving into `analysis_pipeline/` |
| `training/` | Datasets, labelling, model training, and the model and data download scripts |
| `evaluation/` | Tracking quality checks |
| `experiments/` | Ball tracking, Forward-50, jumper numbers: not in the pipeline yet |
| `docs/` | Setup, code inventory and pipeline design |

Start with [`docs/setup.md`](docs/setup.md). [`docs/target_pipeline.md`](docs/target_pipeline.md) explains how the pieces fit together and how a video moves through them.

Quick check after setup:

```bash
python training/download_models.py player_ref_best.pt
python analysis_pipeline/detect_and_track.py data/videos/test_clip_20s.mp4 --max-frames 300
```
