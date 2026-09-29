# Crowd Detection

## Objective

Detect spectators in stadium footage using a YOLO-based crowd detection pipeline.
The module runs person detection on extracted video frames (masked to the crowd
region upstream), saves annotated outputs, and returns structured per-frame results
plus a run summary for density, zoning and behaviour analysis downstream.

## Where It Sits in the Pipeline

```text
video_processing            -> extracts frames + tile metadata
crowd_region_preprocessing  -> attaches one reusable crowd_mask (field/roof masked out)
crowd_detection             -> detect_crowd(focused_video)   <- this module
density_zoning / crowd_behaviour_analytics / ...
```

It is called from `shared/services/crowd_detection_service.py` (`process_detection`)
and from `test_pipeline.py`.

## Models

| File | Role |
|------|------|
| `yolo26mcrowdpeoplefaces.pt` | Main people model: YOLO26m trained on CrowdHuman (people + faces). People are class `1` (`PEOPLE_CLASS_ID`). |
| `yolo26mcrowdpeoplefaces.onnx` | ONNX export of the main model, used for DirectML (`CROWD_DEVICE=dml`). |
| `yolo26mcrowdpeoplefaces_openvino_model/` | OpenVINO export of the main model, used on CPU (`CROWD_DEVICE=cpu`). |
| `yolo26mcrowdpeoplefaces.engine` | Optional TensorRT engine for NVIDIA. Not committed; each machine builds its own (see below). |
| `face_model.pt` | Optional face detector ([YOLOv8-Face-Detection](https://huggingface.co/arnabdhar/YOLOv8-Face-Detection)). Only loaded when `USE_FACE_DETECTION = True`, which is off by default. |
| `yolov8n_crowdhuman.pt` | Earlier people model. The pipeline no longer uses it, but `benchmarking/` still reads it for comparisons. |
| `yolo11n.pt`, `yolo26n.pt` | Base models kept from earlier experiments. |

`.gitignore` excludes model files, so a fresh clone only has `yolo26mcrowdpeoplefaces.pt`.
Build the `.onnx`, OpenVINO and TensorRT exports locally with the commands under
Inference Backends. Without an export, `auto` skips that backend.

## How Detection Works

1. **Crowd mask**: each frame is masked with `crowd_mask` from `crowd_region_preprocessing`, so the field and other non-crowd areas are black.
2. **Tiling**: when `USE_TILING` is on, frames are cut into overlapping tiles using the tile metadata produced by `video_processing`. Each tile is run at `TILE_IMGSZ = 640`, and tiles are processed in batches (`TILE_BATCH`: 16 on GPU, 8 on CPU).
3. **Empty-tile skipping**: tiles that are almost entirely masked out (`MIN_TILE_FILL`) are skipped. This decision is made once per video from the mask itself.
4. **Seam handling and merging**: a box touching an inner tile seam is dropped, because the neighbouring tile's overlap region contains the whole person. Boxes are then mapped back to full-frame coordinates and de-duplicated across tiles with NMS.
5. **Temporal stride**: the detector only runs on every `DETECT_STRIDE`-th frame. The frames in between reuse the previous detections (`"detected": false`), so downstream modules still get one result per frame. Annotated JPEGs are only written for frames where detection actually ran.
6. **Summary**: each run writes `crowd_detection_output/detection_summary_run_NNN.json`, recording backend, device, timings and the peak people count.

## Inference Backends

Select the backend with the `CROWD_DEVICE` environment variable:

| `CROWD_DEVICE` | Backend | Model used |
|----------------|---------|------------|
| `auto` (default) | Picks the fastest backend this machine can run (see below) | as below |
| `cuda:0` | PyTorch/TensorRT on NVIDIA with FP16 | `.engine` if present, otherwise `.pt` |
| `dml` | ONNX Runtime + DirectML, for any DX12 GPU (AMD/Intel) | `.onnx` |
| `cpu` | OpenVINO (roughly 2-4x faster than plain PyTorch on CPU) | `_openvino_model/`, or `.pt` if OpenVINO isn't installed |

`auto` checks in this order and uses the first one that works:

1. **CUDA**: a CUDA build of torch finds an NVIDIA GPU.
2. **DirectML**: `onnxruntime-directml` is installed and the `.onnx` export exists.
3. **OpenVINO on CPU**: `openvino` is installed and the export folder exists.
4. **PyTorch on CPU**: the `.pt` weights.

If you set `cuda` or `dml` explicitly and it isn't available, the pipeline stops with an error explaining how to fix it. Only `auto` falls back silently. The run summary (`backend`, `device`) records which one was chosen.

Setup notes (run from `Crowd_Monitoring/`):

- **CPU**: `pip install -r requirements.txt` is enough. It includes `openvino`; build the OpenVINO export below to use it.
- **CUDA (NVIDIA)**: install `requirements-nvidia.txt` *before* the base requirements, because `pip install ultralytics` otherwise pulls a CPU-only torch:
  ```bash
  pip install -r requirements-nvidia.txt
  pip install -r requirements.txt
  ```
  If a CPU torch is already installed, add `--force-reinstall` to the first command. The file uses cu128, because cu124 has no Python 3.14 wheels; if your driver is too old for cu128, change it to cu126.
- **DirectML (AMD/Intel, Windows)**: remove every other onnxruntime build first, because they install into the same folder and hide the DirectML one. Then install `requirements-amd.txt` (it includes the base requirements) and build the ONNX export:
  ```bash
  pip uninstall -y onnxruntime onnxruntime-gpu onnxruntime-directml
  pip install -r requirements-amd.txt
  ```
  Ultralytics has no DirectML option of its own, so `dml_backend.enable_dml()` patches ONNX Runtime to use `DmlExecutionProvider`. The `dml` setting also sets `YOLO_AUTOINSTALL=false`, which stops Ultralytics from reinstalling plain onnxruntime over it.
- **Ultralytics version**: `requirements.txt` asks for `ultralytics>=8.4.120`. On CUDA the predict call uses `quantize=16` for FP16; on older releases that don't accept `quantize`, `main.py` falls back to `half=True`.
- `config.py` must be imported before `ultralytics`, because it sets `YOLO_VERBOSE` and `YOLO_AUTOINSTALL`. `main.py` already imports it first.

Commands to re-create the exported models (run from `crowd_detection/`):

```bash
# ONNX (DirectML)
yolo export model=yolo26mcrowdpeoplefaces.pt format=onnx imgsz=640 dynamic=True opset=17
# OpenVINO (CPU)
yolo export model=yolo26mcrowdpeoplefaces.pt format=openvino imgsz=640 dynamic=True
# TensorRT (NVIDIA; specific to one GPU, do not commit)
yolo export model=yolo26mcrowdpeoplefaces.pt format=engine imgsz=640 quantize=16 dynamic=True device=0
```

## Configuration

All settings are in `config.py`. The ones marked *env* can be changed without editing the file.

| Setting | Default | Notes |
|---------|---------|-------|
| `CROWD_DEVICE` *(env)* | `auto` | See Inference Backends. |
| `CROWD_DETECT_STRIDE` *(env)* | `30` | Run detection on every Nth frame. `1` = every frame. |
| `CROWD_SKIP_EMPTY_TILES` *(env)* | `true` | Skip tiles that are mostly masked out. |
| `CROWD_DETECT_MAX_WIDTH` *(env)* | `1920` | Written to the run summary. `detect_crowd` does not currently use it to downscale frames. |
| `DEFAULT_CONF` / `DEFAULT_IOU` | `0.20` / `0.30` | Confidence and NMS thresholds. |
| `USE_TILING` | `True` | Tiled detection. Frames without tile metadata fall back to whole-frame detection. |
| `USE_FACE_DETECTION` | `False` | Also run the face model and write face outputs. |
| `SAVE_TILE_DEBUG` | `False` | Save each tile with its kept (green) and dropped-at-seam (red) boxes to `crowd_detection_output/tile_debug/`. |
| `MIN_TILE_FILL` | `0.02` | Minimum fraction of unmasked pixels a tile needs before detection runs on it. |

## Output

`detect_crowd(processed_video)` returns:

```json
{
  "video_id": "match_01",
  "frame_width": 1920,
  "frame_height": 1080,
  "detection_summary": { "run": 9, "backend": "onnx", "device": "dml", "frames_processed": 66, "frames_detected": 3, "ms_per_detected_frame": 443.3, "peak_people_per_frame": 557, "summary_json_path": "..." },
  "frames": [
    {
      "frame_id": 1,
      "timestamp": 0.04,
      "frame_path": "...",
      "people_annotated_frame_path": "crowd_detection_output/people_detection_results/match_01/frame_0001.jpg",
      "face_annotated_frame_path": null,
      "person_count": 412,
      "face_count": null,
      "detection_ms": 443.3,
      "detected": true,
      "people_detections": [{ "bbox": [100, 50, 160, 180], "confidence": 0.93 }],
      "face_detections": []
    }
  ]
}
```

When face detection is off, `face_annotated_frame_path` and `face_count` are `null`.
On frames that reused earlier detections, `people_annotated_frame_path` is `null`
and `detection_ms` is `0`.

Files written, relative to `Crowd_Monitoring/`:

```text
crowd_detection_output/
|- detection_summary_run_NNN.json            # one per run
|- people_detection_results/<video_id>/      # annotated frames (detected frames only)
|- face_detection_results/                   # only when USE_FACE_DETECTION
|- tile_debug/<video_id>/                    # only when SAVE_TILE_DEBUG
```

## Project Structure

```text
crowd_detection/
|- README.md
|- SCHEMA.md
|- config.py                                 # device/backend selection, thresholds, tuning settings
|- main.py                                   # detect_crowd(), tiled detection, NMS, annotation
|- dml_backend.py                            # pins ONNX Runtime to DirectML
|- yolo26mcrowdpeoplefaces.pt / .onnx
|- yolo26mcrowdpeoplefaces_openvino_model/
|- face_model.pt
|- yolov8n_crowdhuman.pt                     # legacy, still used by benchmarking/
|- *.mp4                                     # sample test footage (local only, not in git)
```
