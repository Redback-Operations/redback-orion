# Tracking broadcasts

`scripts/track_video.py` writes an annotated H.264 video and a CSV containing
the source frame number, track ID, class, confidence and bounding box.

## Broadcast-tuned ByteTrack candidate

Wide AFL camera angles contain small detections and longer occlusions than the
default ByteTrack configuration is designed around. A candidate configuration
is provided at `configs/afl_broadcast_bytetrack.yaml`:

```bash
python scripts/track_video.py data/videos/broadcast.mp4 \
  --model models/player_ref_best.pt \
  --tracker configs/afl_broadcast_bytetrack.yaml \
  --conf 0.1
```

In a 300-frame St Kilda–North Melbourne trial using the same detector, the
default configuration produced 1,954 detections and 56 unique IDs. The candidate
produced 2,118 detections and 43 unique IDs. The lower unique-ID count is only a
fragmentation proxy; it is not a measured ID-switch result and should be tested
on more broadcasts before becoming the default.

## Resuming an interrupted long run

Resume into separate part files so existing output is not overwritten. Use the
next source frame, and offset new IDs by at least the maximum ID already present
in the earlier CSV plus one:

```bash
python scripts/track_video.py data/videos/broadcast.mp4 \
  --model models/player_ref_best.pt \
  --tracker configs/afl_broadcast_bytetrack.yaml \
  --conf 0.1 \
  --start-frame 69140 \
  --track-id-offset 10000 \
  --output-suffix _part2
```

The resumed CSV retains absolute source frame numbers. The offset is applied to
both the annotated video labels and CSV IDs. Because the tracker cannot recover
its internal state after a restart, tracks that cross the resume boundary will
still receive a new ID; the offset prevents accidental ID collisions but does
not reconstruct identity continuity.
