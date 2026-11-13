# Crowd Region Preprocessing

## Objective

Prepare extracted stadium frames so downstream crowd detection focuses on visible spectator regions instead of the playing field.

## Approach

- accept extracted frames from `video_processing`
- generate a field exclusion mask
- preserve only the crowd-visible region in a new frame copy
- return the same frame metadata structure expected by `crowd_detection`

## Current Mask Strategy

- use manual polygons when configured
- otherwise detect the green playing field in HSV space
- black out the field region before YOLO person detection runs

## Output

- focused frames saved in `output/focused_frames/`
- updated `frame_path` values for downstream services
- per-frame metadata for field and crowd visibility
