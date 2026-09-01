# Config Folder

This folder stores shared configuration used across services and team tasks.

## What Goes Here

- model paths
- input and output folder paths
- frame sampling values
- detection confidence thresholds
- zone layout settings
- risk classification thresholds

## Example

A file in this folder might define:

- YOLO model path: `models/yolov8.pt`
- frame sample rate: every 5th frame
- detection confidence threshold: `0.5`
- density threshold for high risk: `20 people per zone`

## Why This Folder Matters

Keeping settings here helps the team avoid hardcoding values in many scripts.

If a threshold changes, it can be updated in one place instead of multiple files.
