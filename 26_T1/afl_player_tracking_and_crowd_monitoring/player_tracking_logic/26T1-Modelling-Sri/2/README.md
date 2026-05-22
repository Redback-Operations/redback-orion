# AFL Object Detection with YOLO

This project uses a custom-trained YOLO model to detect AFL-related objects in match footage/images.

## Overview

The pipeline is focused on detecting objects from Sydney Swans vs Western Bulldogs footage. Frames can be extracted from video, then used for training, testing, or running inference with the YOLO model.

The trained model can identify relevant objects in AFL footage and produce detection results such as bounding boxes and class labels.

## Files

- `best(SS_vs_WB).pt` — trained YOLO model weights for the Sydney Swans vs Western Bulldogs dataset
- `extract_frames.py` — extracts frames from video footage for dataset creation or testing
- `notebook(SS_vs_WB).ipynb` — notebook used for training, testing, or experimentation

## Usage

Use `extract_frames.py` to extract frames from an input video:

```bash
python extract_frames.py