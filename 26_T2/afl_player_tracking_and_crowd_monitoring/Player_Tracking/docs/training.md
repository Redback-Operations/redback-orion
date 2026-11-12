# Training Results (T2 2026)

Recipe (from T1): yolo11s pretrained, 50 epochs, imgsz 640, batch 16,
patience 10, seed 42. Trained locally on RTX 3080 via `scripts/train.py`.
Weights copied to `models/`; full runs in `runs/detect/`.

## all_teams (7 classes)

Early stopped at epoch 44 (best: epoch 34). Val: 114 images, 1,068 boxes.

| Class | P | R | mAP@50 | mAP@50-95 |
|---|---|---|---|---|
| all | 0.807 | 0.807 | 0.817 | 0.346 |
| CAR | 0.919 | 0.923 | 0.942 | 0.462 |
| GCS | 0.899 | 0.939 | 0.954 | 0.465 |
| HAW | 0.826 | 0.879 | 0.898 | 0.376 |
| CAT | 0.856 | 0.870 | 0.913 | 0.409 |
| REF | 0.790 | 0.835 | 0.823 | 0.340 |
| SS | 0.730 | 0.592 | 0.606 | 0.181 |
| WB | 0.630 | 0.611 | 0.581 | 0.193 |

- SS and WB are the weak classes (~0.6 mAP@50). Sydney Swans (red/white) and
  Western Bulldogs (red/white/blue) have similar jerseys — likely mutual
  confusion, and they only appear in one match's footage (194 images).
- T1's unified model reported 0.949 mAP@50, but that was a different class
  set (BALL/POST, no SS/WB) on their own split — not directly comparable.

## player_ref (2 classes)

Early stopped at epoch 39 (best: epoch 29). Val: 114 images, 1,068 boxes.

| Class | P | R | mAP@50 | mAP@50-95 |
|---|---|---|---|---|
| all | 0.828 | 0.801 | 0.829 | 0.354 |
| PLAYER | 0.843 | 0.792 | 0.849 | 0.361 |
| REF | 0.813 | 0.811 | 0.810 | 0.347 |

- REF recall (0.811) is healthy despite the 7:1 class imbalance — no
  rebalancing needed for now.

## all_classes (9 classes)

Early stopped at epoch 43 (best: epoch 33). Val: 114 images, 1,110 boxes.

| Class | P | R | mAP@50 | mAP@50-95 |
|---|---|---|---|---|
| all | 0.786 | 0.778 | 0.789 | 0.338 |
| CAR | 0.893 | 0.923 | 0.953 | 0.462 |
| GCS | 0.916 | 0.934 | 0.928 | 0.443 |
| HAW | 0.797 | 0.861 | 0.854 | 0.357 |
| CAT | 0.866 | 0.902 | 0.938 | 0.406 |
| REF | 0.858 | 0.820 | 0.829 | 0.328 |
| SS | 0.662 | 0.585 | 0.565 | 0.176 |
| WB | 0.734 | 0.676 | 0.640 | 0.208 |
| BALL | 0.607 | 0.667 | 0.611 | 0.288 |
| POST | 0.738 | 0.639 | 0.785 | 0.373 |

- This is the closest variant to T1's `best_unified.pt` (P 0.930, R 0.880,
  mAP@50 0.949, mAP@50-95 0.510) — theirs had the same BALL/POST classes but
  no SS/WB, and was evaluated on their own split. On shared classes ours is
  in range for CAR/GCS/CAT but behind on HAW/REF.
- BALL (0.611 on only 6 val boxes) and POST (0.785) are usable but thin —
  more labelled examples would help both.
- SS/WB remain the weakest classes, as in `all_teams`.

## Next steps

- More SS/WB footage (or a second match) would likely fix the weak classes.
- If team identity doesn't matter for the tracking pipeline, `player_ref`
  is the stronger and simpler detector.
