# Datasets

Built by `scripts/build_datasets.py` from `data/raw/` into `datasets/`.
All splits are 80/20 train/val, shuffled with seed 42 (same as T1).
Each dataset folder has `train/`, `val/`, and a `data.yaml` ready for
`model.train(data=...)`.

Only the two combined datasets are built; per-match variants live only in
`data/raw/`. Files are prefixed with the source dataset
(e.g. `ss_vs_wb__012f0df2-01.jpg`) to avoid name collisions.

| Dataset | Train/Val | Boxes | Classes |
|---|---|---|---|
| `all_teams` | 456/114 | 5,254 | CAR(0) GCS(1) HAW(2) CAT(3) REF(4) SS(5) WB(6) |
| `all_classes` | 456/114 | 5,397 | CAR(0) GCS(1) HAW(2) CAT(3) REF(4) SS(5) WB(6) BALL(7) POST(8) |
| `player_ref` | 456/114 | 5,254 | PLAYER(0) REF(1) |

Notes:

- `all_teams` is 7 classes: the four T1 teams + SS/WB (which T1 never merged
  into their unified model) + REF. BALL(29) and POST(114) boxes are dropped —
  too thin to train. This means it is NOT directly comparable to T1's
  `best_unified.pt`, which had BALL/POST instead of SS/WB.
- `player_ref` drops the same BALL/POST boxes; every team class maps to
  PLAYER. Class balance: 4,599 PLAYER vs 655 REF — REF is the minority class,
  so check per-class recall when evaluating.
- `ss_vs_wb` has 11 images with empty label files (background images) — kept
  intentionally.
