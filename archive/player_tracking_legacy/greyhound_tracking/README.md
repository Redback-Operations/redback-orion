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
 [View our project on Roboflow](https://universe.roboflow.com/greyhound-tracking-ioamr/australian-greyhound-racing)

 Below is a video showing our model in action, demonstrating its ability to accurately detect and track greyhounds in a training video: 
 
  [Trained model deployed on 1080p video](https://drive.google.com/file/d/1vuD1QAQ0299rSBFMwKHn4vVC6XpA2SUN/view?usp=drive_link)
  
  This visual showcases how the model consistently identifies greyhounds, tracks them across frames, and calculates their relative speeds, providing valuable insights during races.
  
  Some screenshots showcasing the output : 
  
  ![image](https://github.com/user-attachments/assets/82443ceb-1e74-4b2f-8cee-888457ba3a9c)
  ![image](https://github.com/user-attachments/assets/400c425e-ebfa-4637-9503-39d1baad1099)
  ![image](https://github.com/user-attachments/assets/10db37da-8dac-41b6-977b-3b98dc3bd3b4)




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

- [Input video for testing](https://drive.google.com/file/d/1m7OB1YPR9YYxoBQdoUmsBIx5SL1jvDdO/view?usp=sharing)


## Speed Calculation Method
The speed of greyhounds is estimated using the following steps:
1. **Detection**: YOLOv8 detects greyhounds in each video frame.
2. **Tracking**: DeepSort tracks detected greyhounds, assigning a unique ID to each.
3. **Position Tracking**: The center of each bounding box is recorded across frames.
4. **Speed Estimation**: Speed is calculated by measuring the Euclidean distance between positions in consecutive frames and multiplying by the frame rate (FPS).

**Get Speed Estimates:**
- The speed calculation is done using the distance between bounding boxes across frames and converting it to px/s and km/h. You can view the implementations given below:
- [feature_pixel_per_second.ipynb](feature_pixel_per_second.ipynb)

- [feature_kilometer_per_hour.ipynb](feature_km_per_hour.ipynb)

 ## Speed Calculation Method (UPDATED) ([speed_estimation_final.ipynb](speed_estimation_final.ipynb))
 This method calculates the speed of each detected greyhound in pixels per second (pixels/s).

1.  **Detection**: The YOLOv8 model (`best (3).pt` or your specified model) is used to detect greyhounds in each frame of the input video.
2.  **Tracking**: The ByteTrack algorithm (`tracker="bytetrack.yaml"`) is employed to track each detected greyhound across consecutive frames. Each tracked greyhound is assigned a unique `track_id`. For display purposes, these `track_id`s are mapped to simpler labels like "dog_1", "dog_2", etc.
3.  **Position Logging**: For each tracked greyhound, the center coordinates `(center_x, center_y)` of its bounding box are recorded in every frame it appears. A history of these positions (frame number, x, y) is maintained for each `track_id` (up to the last 30 positions).
4.  **Speed Calculation**:
    * **Time Interval**: The time elapsed between consecutive frames is calculated as $ \frac{1}{FPS} $, where FPS is the frames per second of the video. This is calculated once at the beginning.
    * **Pixel Distance**: If a greyhound is tracked for at least two frames, the Euclidean distance between its current center position (`current_pos_pixel`) and its previous center position (`prev_pos_pixel`) is calculated:

    * **Pixel Distance**: If a greyhound is tracked for at least two frames, the Euclidean distance between its current center position (`current_pos_pixel`) and its previous center position (`prev_pos_pixel`) is calculated:
      
       ![image](https://github.com/user-attachments/assets/d257cacd-972d-47b8-911d-008c432df127)

    * **Pixel Speed**: The speed in pixels per second is then estimated as:
       ![image](https://github.com/user-attachments/assets/49a40b6a-751c-4a06-952b-2366a8e09260)

      
5.  **Annotation & Output**:
    * The original video frames are annotated with bounding boxes around detected greyhounds.
    * A text label is displayed near each bounding box, showing the assigned dog label and its calculated speed (e.g., "dog_1: 150.5 pixels/s").
    * The processed frames are compiled into an output video file named `pixel_speed_estimation.avi`.
    * [Link to output video] (https://drive.google.com/file/d/1TLh9Cm2t7bD5YQzE0xjnMGPdO5FYcuXP/view?usp=sharing) 
      ![image](https://github.com/user-attachments/assets/730c32b9-8b56-4d57-9b08-bc0f0df6b061)

 

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

## Data Collection
All data was collected off broadcast tv in Australia which is covered by the Australian Educational Licence which is held by Deakin University. Only data used by this collection method was used to train our model.
- [Screenrights](https://www.screenrights.org/screen-audiences/screenrights-licences/australian-educational-licences/)
- [Copyright](https://www.copyright.com.au/licences-permission/educational-licences/)

## Contributors :sparkles:
- [*Harsh Bhanot*](https://github.com/HarshBhanot7)
- [*Mohitpreet Singh*](https://github.com/plasma141)
- [*Chris Abbey*](https://github.com/rissicay)

## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/Redback-Operations/redback-documentation/blob/main/LICENSE) file for details.

## Acknowledgements
We would like to extend our gratitude to the following:

- **YOLOv8 and Ultralytics Communities:** Thank you for your contributions to the field of object detection and tracking. Your work has been instrumental in the development of our project.
- **ByteTrack Authors:** For the robust tracking algorithm used in this project.
- **Roboflow:** Special thanks for providing platform and annotation tools that have significantly contributed to the accuracy and efficiency of our model.
