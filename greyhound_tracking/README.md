---
sidebar_position: 1
---

# Greyhound Detection and Tracking Project
![readme style: standard](https://img.shields.io/badge/readme%20style-standard-brightgreen)
![Roboflow](https://img.shields.io/badge/Roboflow-Model%20Status-blue)
![Python](https://img.shields.io/badge/Python-3.12-blue)

## Overview
This project focuses on detecting and tracking greyhounds in races for object detection and tracking. The system highlights all the dogs in each video frame by putting a bounding box around them or identifying their number. Additionally, it calculates their relative speeds.

## Features
- **Greyhound Detection:** Accurately detects and identifies all greyhounds in each video frame.
- **Tracking and Sorting:** Tracks the positions of the greyhounds throughout the race.
- **Bounding Boxes:** Draws consistent bounding boxes around detected greyhounds.
- **Speed Calculation:** Calculates the relative speed of each greyhound in the race.
- **Custom Dataset:** Created and labeled a large custom dataset using Roboflow, with tasks distributed among team members for efficient data labeling.

## Model in Action✅
- [View our project on Roboflow](https://universe.roboflow.com/greyhound-tracking-ioamr/australian-greyhound-racing)
- Below is a video showing our model in action, demonstrating its ability to accurately detect and track greyhounds in a training video: 
 
  [Trained model deployed on 1080p video](https://drive.google.com/file/d/1vuD1QAQ0299rSBFMwKHn4vVC6XpA2SUN/view?usp=drive_link)
  
  This visual showcases how the model consistently identifies greyhounds, tracks them across frames, and calculates their relative speeds, providing valuable insights during races.

## Test Our Public Model
You can test our public model by uploading your own videos to see how well it detects and tracks greyhounds in action. Use the link below to upload a video and test the model:

- [Test Our Model](https://universe.roboflow.com/greyhound-tracking-ioamr/australian-greyhound-racing/model/10)

Simply upload a video, and the model will process it, highlighting greyhounds with bounding boxes and tracking their movements throughout the race.

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
2. **Run the Project on Google Colab:**
   - We have provided a Google Colab notebook that sets up everything you need, including accessing the dataset directly from Roboflow. Click the link below to open the notebook and follow the instructions to run the project:

   - [Run on Google Colab](colab_training.ipynb)
     
3. **Download the Dataset:**
   - If you prefer running the project locally, use the [Roboflow dataset link](https://app.roboflow.com/ds/TYmihJNfyP?key=D4ylby1lBR) to download the training data.
      
4. **Setup YOLOv8:**
   - Follow the [YOLOv8 installation guide](https://docs.ultralytics.com/models/yolov8/) to set up the detection model.

5. **Run the Detection Model:**
    - Use the following command to run the detection model:
    ```bash
    python detect.py --source path_to_your_video --weights yolov8s.pt --conf 0.25
    ```

## Dataset
The dataset used for training the model includes a large collection of images of greyhounds, labeled and annotated using Roboflow. The dataset was created by the team, with tasks distributed among members to efficiently label each image, ensuring a high-quality dataset to improve the model's performance.

- [View our Roboflow Datasets](https://universe.roboflow.com/greyhound-tracking-ioamr/australian-greyhound-racing/dataset/10)


## Speed Calculation Method
The speed of greyhounds is estimated using the following steps:
1. **Detection**: YOLOv8 detects greyhounds in each video frame.
2. **Tracking**: DeepSort tracks detected greyhounds, assigning a unique ID to each.
3. **Position Tracking**: The center of each bounding box is recorded across frames.
4. **Speed Estimation**: Speed is calculated by measuring the Euclidean distance between positions in consecutive frames and multiplying by the frame rate (FPS).

**Get Speed Estimates:**
- The speed calculation is done using the distance between bounding boxes across frames and converting it to km/h. You can view the implementation in the [speed_test.ipynb](speed_test.ipynb)

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

## Getting Added to the Roboflow Project
If you'd like to contribute or use our dataset for your own projects, you can request access to our Roboflow project. Here's how:

1. **Request Access:** Reach out to any of the project contributors via GitHub, with the subject line "Roboflow Access Request".
2. **Join the Roboflow Team:** Once your request is approved, you'll receive an invite to join the Roboflow project. Accept the invitation to gain access to the dataset and project resources.
3. **Access the Dataset:** After joining, you'll be able to view, download, and contribute to the dataset on Roboflow.

## Contributors :sparkles:
- [*Harsh Bhanot*](https://github.com/HarshBhanot7)
- [*Mohitpreet Singh*](https://github.com/plasma141)
- [*Chris Abbey*](https://github.com/rissicay)

## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/HarshBhanot7/redback-documentation/blob/main/LICENSE) file for details.

## Acknowledgements
We would like to extend our gratitude to the following:

- **YOLOv8 and Ultralytics Communities:** Thank you for your contributions to the field of object detection and tracking. Your work has been instrumental in the development of our project.
- **Roboflow:** Special thanks for providing platform and annotation tools that have significantly contributed to the accuracy and efficiency of our model.
