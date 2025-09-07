# Pose Estimation Fitness Project

## Overview
This project uses a pose estimation pipeline for fitness applications. It leverages a pre-trained Keypoint R-CNN model to detect keypoints, visualize poses, and evaluate exercise form.

## Setup Instructions
1. Clone the repository.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Features
- **Pose Estimation**: Detects keypoints using a pre-trained Keypoint R-CNN model.
- **Strain Analysis**: Calculates strain metrics for various exercises (e.g., deadlift, bench press, squat).
- **Visualization**: Draws poses and highlights areas of high strain.
- **CSV Export/Import**: Saves and loads strain results to/from CSV files.
- **Best/Worst Form Analysis**: Identifies and displays the best and worst exercise forms based on strain metrics.
- **Graphical Output**: Generates strain metric graphs for visualization.

## Usage
Run the main script to evaluate exercise form:
```
python src/main.py
```

### Workflow
1. Select an exercise type (e.g., deadlift, bench press, squat).
2. Load images from the `dataDeadlift` directory.
3. Analyze and visualize poses with strain metrics.
4. Display the best and worst exercise forms with corresponding strain graphs.

## Objectives
- Provide a streamlined workflow for detecting and visualizing poses.
- Evaluate exercise form and highlight areas of improvement.

## Contributions
Contributions to this project are welcome. Please submit a pull request or open an issue for discussion.

## To-Do
- Add support for additional exercises (e.g., lunges, pull-ups, push-ups).
- Implement dynamic limb pair definitions for new exercises.
- Enhance strain calculation logic to accommodate different exercise types.
- Create a configuration file for exercise-specific parameters (e.g., thresholds, keypoint mappings).
- Add unit tests for new exercise types to ensure accuracy.
- Improve visualization for multi-person exercises.
