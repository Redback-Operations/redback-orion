# Ball Detection Pilot

## Objective

This pilot investigates whether ball detection can be improved before adding
ball tracking and trajectory generation to the T2 player-tracking pipeline.

The ball requires separate investigation because it is smaller than a player,
moves quickly, can be blurred, and is frequently occluded by players.

## Existing Model Baseline

The existing `all_classes_best.pt` model includes `BALL` as class 7.

It was tested on a 20-second CAR-GCS broadcast clip containing 598 frames. The
ball was visibly present, but the model produced no ball detections:

- zero detections at a confidence threshold of 0.05;
- zero detections when inference resolution was increased to 1280 pixels;
- zero detections in a close crop containing the visible ball at a confidence
  threshold of 0.01.

Player and referee detections were still produced, suggesting that ball
detection, rather than video loading or general inference, was the immediate
bottleneck.

## Dataset Finding

The existing T2 dataset documentation reports 29 `BALL` annotations in the
`all_classes` dataset. These annotations come from CAT-HAW footage, while the
baseline test used CAR-GCS footage.

This limited quantity and match variety may explain why the model did not
generalise to the test clip. More varied data is required before evaluating
tracking methods.

## CAR-GCS Labelling Pilot

A one-class labelling pilot was completed using:

```text
0 = BALL
```

Fifty CAR-GCS images were reviewed using a consistent rule: label only the
active match ball when its visible location can be identified without guessing.
Spare balls, balls held by attendants, logos and shadows were ignored.

Pilot outcome:

| Outcome | Images |
|---|---:|
| Positive images with one BALL box | 29 |
| Negative images with no visible active ball | 14 |
| Uncertain images held back for review | 7 |
| Total reviewed | 50 |

The 43 completed images were exported in YOLO format. Validation of the export
confirmed:

- 43 matching image and label files;
- 29 BALL boxes;
- all class IDs were 0;
- all normalised coordinates were within YOLO bounds;
- no invalid YOLO annotation rows.

The uncertain images were not included as negatives because doing so could
teach the model that a heavily occluded ball is background.

## Training Pipeline Check

The verified data was separated into:

- 34 training images: 23 positive and 11 negative;
- 9 validation images: 6 positive and 3 negative.

A one-epoch smoke test was run from `all_classes_best.pt` at an image size of
960 pixels. The test:

- loaded all training and validation data successfully;
- found no corrupt images or labels;
- changed the copied model from nine classes to the single BALL class;
- transferred 493 of 499 compatible pretrained weight items;
- completed training and validation;
- saved separate `best.pt` and `last.pt` experiment weights.

Precision, recall and mAP were zero after this single epoch. This run was only a
pipeline check and is not treated as a model-quality result.

## Limitations

- The new pilot images come from one CAR-GCS match.
- The validation images come from the same match as the training images.
- The dataset is too small to support a reliable generalisation claim.
- The seven uncertain examples still require team review.
- Local videos, datasets and trained weights are not stored in Git.

## Next Steps

1. Add labelled examples from at least one different match.
2. Review a small calibration batch with the team before scaling annotation.
3. Keep a separate match or clip as a true hold-out test set.
4. Train a ball-only pilot model and compare it with the existing model using
   the same footage and inference settings.
5. Investigate temporal tracking and trajectory output only after detection is
   sufficiently reliable.

