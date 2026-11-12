# Broadcast model regression: 9 September 2026

The failed broadcast run trained on an incomplete local copy of the original
dataset. Missing annotation files were silently interpreted as backgrounds.
This is a concrete training-data fault, not evidence that a grass filter is
required to learn broadcast football.

## Evidence from the actual run

`runs/detect/broadcast/args.yaml` points to `datasets/player_ref_broadcast/data.yaml`.
That YAML combined `datasets/player_ref/train/images` with the 84 reviewed
St Kilda/North Melbourne frames. It did not reference the 1,689 unreviewed
broadcast frames. But merely checking those paths missed the broken contents.

The training cache, formerly at
`data/raw/broadcast_stkilda_northmelbourne/reviewed/labels.cache`, records the
combined image list. Its result tuple was `(104, 81, 2, 0, 185)`:
104 annotation files found, 81 missing, 2 explicitly empty, 0 corrupt, 185 images.

| Source | Expected images | Actual training images | Images with label files |
|---|---:|---:|---:|
| Original player/ref train | 456 | 101 | 20 |
| Reviewed broadcast | 84 | 84 | 84 |
| Total | 540 | 185 | 104 |

The local old training directory also had 132 annotation files whose images
were absent. The download was incomplete on both sides.

Cross-checking the 81 missing-label images against the original Linux
`datasets/all_classes/train/labels.cache` shows that **80 contain players/refs,
totalling 869 player/ref boxes**. Those objects became unlabelled backgrounds in
the failed training run. This is direct conflicting supervision. The local
Ultralytics `data/utils.py::verify_image_label` explicitly produces an empty
box array when the annotation file is missing.

The exact reason the earlier download was incomplete is not recorded. It is
not established that an auto-labeller added crowd labels to these old images.

This also disproves the previous agent's claim that the merged YAML guaranteed
the original training data was present. A path can exist while most of its
image/annotation pairs are missing.

## Model comparison

Both checkpoints were re-evaluated in the same installed runtime
(Ultralytics 8.4.137, Torch 2.13.0, CPU, 640px, batch 8), on the same complete
114-image original validation set, containing 1,068 boxes.

| Checkpoint | Precision | Recall | mAP50 | mAP50–95 |
|---|---:|---:|---:|---:|
| `models/player_ref_best.pt` | 0.8264 | 0.8075 | 0.8292 | 0.3523 |
| `runs/detect/broadcast/weights/best.pt` | 0.7140 | 0.3369 | 0.2651 | 0.0675 |

The failed run's best checkpoint is from **epoch 1**, not a mature 50-epoch
model. Its CSV ends at epoch 11 after ten epochs without a better fitness.
Both mAP and validation classification loss fluctuate badly afterwards.
Its initial weights were generic `yolo11s.pt`, so it did not preserve the
original model's learned player/ref detector through fine-tuning.

On broadcast frame 150, at identical 640px / 0.4 confidence settings without
tracking or grass filtering, the original emits 12 boxes and the failed model
26, including duplicate boxes and the yellow official classified as PLAYER.
That frame demonstrates defects beyond merely detecting spectators; these
counts alone are not precision/recall measurements.

Changing the training environment (original checkpoint: Ultralytics 8.4.103,
Linux/CUDA; failed run: 8.4.137 on macOS) is another uncontrolled variable.
There is no evidence here proving a hardware/library bug. The bad annotations
are established; the exact fraction of the regression attributable to each
other setting would require controlled ablations.

There was no broadcast validation data in the failed run. Its metric could not
measure broadcast improvement. The separate reviewed-only YAML also pointed
train and validation to the same images; that YAML was not the failed run's
selected dataset, but was unsafe for the documented next training command.

The current review manifest contains 104 approved frames, while the exported
folder still contained only 84. After refreshing the export, the last 20
approved frames (288 boxes) provide a small within-match holdout that was not
in the failed run's training cache. Both existing models were evaluated on it:

| Checkpoint | Broadcast mAP50 | PLAYER AP50 | REF AP50 |
|---|---:|---:|---:|
| Original player/ref | 0.7488 | 0.8248 | 0.6728 |
| Failed broadcast | 0.4724 | 0.8247 | 0.1201 |

The failed model's referee discrimination is particularly poor. Similar player
AP50 does not mean identical visual output: the failed model has a different
precision/recall tradeoff and duplicate detections. This holdout is only 20
frames from one match, not a broad broadcast benchmark.

## Repairs

- Training preflight now requires every image to have a label file, permits
  intentional empty labels, rejects orphan labels and invalid class/box values,
  and detects identical images across train/validation by SHA-256.
- Each new run saves an image/label hash snapshot so future investigations can
  establish what actually entered training.
- The builder requires complete original raw data before writing any dataset.
  Broadcast builds read only the three named original raw sources and explicit
  `reviewed/` exports whose files match their `reviewed.txt` manifests.
- A fresh broadcast dataset preserves the original 456/114 split and holds
  out the last 20% of the reviewed broadcast frames, excluding training frames
  within 300 source frames of that holdout. This is a within-match development
  holdout; a separate reviewed match is still needed for generalisation testing.
- `--fine-tune` starts from `models/player_ref_best.pt`, uses explicit AdamW at
  0.0001 (rather than auto optimizer overriding a manual LR), and disables
  mosaic with a smaller scale range. This is a conservative starting recipe,
  not a claimed optimal hyperparameter choice.
- Review approval now saves edits first. Empty reviewed frames overwrite old
  boxes with an empty label. Re-exporting removes stale reviewed copies after
  an approval is revoked. Reviewed exports no longer declare self-validation.

## Completed recovery and verification

Restored all 1,089 missing original raw files from the project's public Drive
backup without overwriting existing originals. The three sources now contain
200 GCS/CAR, 194 SS/WB and 176 CAT/HAW matched pairs. Every restored/built image
passed an image corruption check.

Refreshed the reviewed export to 104 approved frames (1,669 remain unreviewed).
No existing exported label differed from its canonical raw label before the
refresh; the previous 84-frame export and manifest were backed up first.

Built `datasets/player_ref_broadcast_clean/data.yaml`:

- **535 train** = 456 original + 79 reviewed broadcast frames; 4,941 boxes.
- **134 val** = 114 original + 20 held-out broadcast frames; 1,356 boxes.
- Five reviewed frames excluded to provide the temporal gap.
- 12 explicit background images across both splits; zero missing labels.
- Original train/val membership exactly matches the saved Linux caches.
- All original 114 validation images and label files are unchanged.
- All 669 output images verified; preflight finds no train/val image overlap.
- 12 regression/existing tests pass; `git diff --check` is clean.

The old incomplete built datasets remain available as diagnostic evidence;
use the new `player_ref_broadcast_clean` dataset for retraining. No replacement
model has been trained or promoted during this investigation.

The existing optional grass filter is not a model repair. Counting fewer
detections or inspecting one filtered frame cannot establish that all removed
boxes were spectators and all players were retained. Its previous blanket
claims were not supported by a labelled evaluation.

## Local evidence artifacts

`outputs/broadcast_diagnosis/` contains the untouched original training cache,
its JSON inventory, the 81 missing-label images matched against original ground
truth, matched validation metric JSONs, and a same-frame detector comparison.
The original failed weights and original production weights remain intact.

See the README for the rebuild, preflight and fine-tuning commands. A repaired
dataset and tested scripts alone do not prove a replacement model is better:
validate a retrained checkpoint on both domains before promoting it.

Ultralytics references: [training settings](https://docs.ultralytics.com/modes/train/)
and [fine-tuning guidance](https://docs.ultralytics.com/guides/finetuning-guide/).
