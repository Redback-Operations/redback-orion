
---
sidebar_position: 1
---

# Greyhound Detection and Tracking Project
![readme style: standard](https://img.shields.io/badge/readme%20style-standard-brightgreen)
![Roboflow](https://img.shields.io/badge/Roboflow-Model%20Status-blue)
![Python](https://img.shields.io/badge/Python-3.12-blue)

## Overview
This project focuses on detecting and tracking greyhounds in races using YOLOv8 for object detection and tracking. The system highlights all the dogs in each video frame by putting a bounding box around them or identifying their number. Additionally, it calculates their relative speeds.

### Features
- **Greyhound Detection:** Accurately detects and identifies all greyhounds in each video frame.
- **Tracking and Sorting:** Tracks the positions of the greyhounds throughout the race.
- **Bounding Boxes:** Draws consistent bounding boxes around detected greyhounds.
- **Speed Calculation:** Calculates the relative speed of each greyhound in the race.
- **Custom Dataset:** Created and labeled a large custom dataset using Roboflow, with tasks distributed among team members for efficient data labeling.

### Watch the Project in Action
- [View our project on Roboflow](https://universe.roboflow.com/greyhound-tracking-ioamr/australian-greyhound-racing)
- [Relative speed of greyhounds](https://github.com/rissicay/redback-orion/blob/main/greyhound_tracking/notebooks/speed_test.ipynb)

## Table of Contents
1. [Overview](#overview)
    - [Features](#features)
2. [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Steps](#steps)
3. [Speed Calculation](Speed-Calculation-Method)
4. [Dataset](#dataset)
5. [Challenges and Solutions](#challenges-and-solutions)
6. [Future Work](#future-work)
7. [Contributing](#contributing)
8. [Contributors](#contributors)
9. [License](#license)
10. [Acknowledgements](#acknowledgements)

## Installation

### Prerequisites
- NumPy
- Matplotlib
- Ultralytics
- OpenCV
- Keras
- Graphviz
- Pydot

### Steps
1. **Clone the Repository:**
    ```bash
    git clone https://github.com/rissicay/redback-orion
    ```
2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Download the Dataset:**
    - Use the [Roboflow dataset link](https://app.roboflow.com/ds/TYmihJNfyP?key=D4ylby1lBR) to download the training data.
4. **Setup YOLOv8:**
    - Follow the [YOLOv8 installation guide](https://docs.ultralytics.com/models/yolov8/) to set up the detection model.

5. **Run the Detection Model:**
    - Use the following command to run the detection model:
    ```bash
    python detect.py --source path_to_your_video --weights yolov8s.pt --conf 0.25
    ```
6. **Get Speed Estimates:**
    - The speed calculation is done using the distance between bounding boxes across frames and converting it to km/h. You can view the implementation in the [speed_test.ipynb](https://github.com/rissicay/redback-orion/blob/main/greyhound_tracking/notebooks/speed_test.ipynb).

## Dataset
The dataset used for training the model includes a large collection of images of greyhounds, labeled and annotated using Roboflow. The dataset was created by the team, with tasks distributed among members to efficiently label each image, ensuring a high-quality dataset to improve the model's performance.

- [View our Roboflow repository](https://universe.roboflow.com/greyhound-tracking-ioamr/australian-greyhound-racing)


## Speed Calculation Method
The speed of greyhounds is estimated using the following steps:
1. **Detection**: YOLOv8 detects greyhounds in each video frame.
2. **Tracking**: DeepSort tracks detected greyhounds, assigning a unique ID to each.
3. **Position Tracking**: The center of each bounding box is recorded across frames.
4. **Speed Estimation**: Speed is calculated by measuring the Euclidean distance between positions in consecutive frames and multiplying by the frame rate (FPS).

## Challenges and Solutions
- **Close Proximity Detection:** Initial challenges included difficulties in detecting greyhounds when they were close together. This was mitigated by expanding the dataset and refining the model.
- **Obstruction Issues:** Detecting greyhounds behind railings or other obstacles required additional training data and fine-tuning of the model.
- **Speed Calculation:** The speed feature was added to the system, but it requires further refinement to ensure accurate measurements. The method involves calculating the distance moved by the bounding boxes of greyhounds across frames and converting it to speed in km/h.

## Future Work
- **Further Model Refinement:** Continue refining the model to enhance accuracy and robustness.
- **Speed Feature Improvement:** Improve the speed calculation feature for more accurate real-time tracking.
- **Automated Testing Pipeline:** Implement an automated testing pipeline to validate the model against new datasets.
- **Extended Features:** Explore adding features such as live commentaries.

## Contributing
Contributions are welcome! Please follow the standard contribution guidelines:

1. Fork the repository from [GitHub](https://github.com/rissicay/redback-orion).
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## Contributors :sparkles:
- [*Harsh Bhanot*](https://github.com/HarshBhanot7)
- [*Mohitpreet Sing*](https://github.com/plasma141)
- [*Chris Abbey*](https://github.com/rissicay)

## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/HarshBhanot7/redback-documentation/blob/main/LICENSE) file for details.

## Acknowledgements
We would like to extend our gratitude to the following:

- **YOLOv8 and Ultralytics Communities:** Thank you for your contributions to the field of object detection and tracking. Your work has been instrumental in the development of our project.
- **Roboflow:** Special thanks for providing platform and annotation tools that have significantly contributed to the accuracy and efficiency of our model.