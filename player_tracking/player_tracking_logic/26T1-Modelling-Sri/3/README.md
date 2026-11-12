# Geelong Cats vs Hawthorn Detection with YOLO

This project uses a custom-trained YOLO model to detect objects in Geelong Cats vs Hawthorn AFL footage or images.

## Overview

The model was trained on a Geelong Cats vs Hawthorn dataset and is designed to detect selected AFL-related classes. YOLO processes each image or video frame and returns bounding boxes, class labels, and confidence scores.

During dataset preparation, unwanted classes such as ball and post were ignored so the model focuses only on the required detection classes.

## Files

- `best(CAT_vs_HAW).pt` — trained YOLO model weights for the Geelong Cats vs Hawthorn dataset
- `notebook(CAT_vs_HAW).ipynb` — notebook used for dataset preparation, training, testing, and model evaluation
- `README.md` — project documentation

## Model

The model file `best(CAT_vs_HAW).pt` is a custom YOLO model trained to detect selected classes from the dataset.

The final detection classes are:

- `CAT` — Geelong Cats player
- `HAW` — Hawthorn player
- `REF` — referee/umpire

## Output

The project can produce:

- YOLO detection results
- Bounding boxes
- Class labels
- Confidence scores
- Trained model weights

## Notes

Detection performance depends on image quality, object visibility, occlusion, camera angle, and how closely new input data matches the training dataset.