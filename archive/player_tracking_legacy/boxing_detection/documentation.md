# Boxing Detection Project Documentation

## Contributor

Vignesh Senthilnathan [@senduz](https://github.com/senduz)

  

## Motivation

- The primary motivation for this project is to develop an efficient and accurate system for detecting hits in boxing training videos. This system aims to help athletes and trainers analyze and improve their performance by providing automated hit detection.

- The project addresses the problem of manual analysis, which is time-consuming and prone to errors, by utilizing computer vision techniques to automate the detection and counting of hits.

  

## Data and Model Sources

-  **Data Sources:**

Datasets used in this project were sourced from Roboflow, including:

- [Project Boxing](https://universe.roboflow.com/goodgoose/project-boxing-qwxns)

- [Boxing Gloves Detection](https://universe.roboflow.com/boxing-uuhxl/boxing-gloves-detection)

- [Boxing Gloves Detection Computer Vision Project](https://universe.roboflow.com/boxing-uuhxl/boxing-gloves-detection)

- [Boxing club Computer Vision Project](https://universe.roboflow.com/ie/boxing-club)

- [Boxing Detected](https://universe.roboflow.com/computer-vision-jrnie/boxing-detected)

-  **Model Sources:**

The project utilizes the YOLOv8 model, a state-of-the-art object detection algorithm, to perform hit detection.

  

## Methodology

- The project uses the YOLOv8 model for detecting objects (e.g., boxing gloves) in video frames. There are three parts:

- Live video boxing glove detection:

- Training and using the trained YOLOv8 model to detect boxing gloves in each frame in real-time.

- Display the video feed with bounding boxes around detected gloves, along with confidence scores and labels, to provide visual feedback of detection.

- Boxing bag detection and hit counting:

- Use roboflow dataset containing boxing bag and glove images to train the YOLOv8 model.

- Train the model to detect the boxing gloves and the boxing bag in the video frames.

- Implement a collision detection algorithm to count the number of hits on the boxing bag.

- Implement a cooldown mechanism to avoid counting multiple hits in the consecutive frames.

- Boxers hit detection, head shot and body shot counting.

- Use roboflow dataset that contains boxer, boxing gloves, face and body images.

- Train and implement a YOLOv8 model to detect classes.

- Implement a collision detection algorithm that checks for collision between the bounding boxes of the boxing gloves with the head and body of the fighter.

- Implement a cooldown mechanism to avoid counting multiple hits in the consecutive frames.

  
  

## Challenges and Solutions

-  **Challenges:**

- Inaccurate detection of gloves due to it moving quite fast during punches.

- Object detection alone was not enough to classify punches in the boxing bag hit detection project.

- Multiple hits were detected in consecutive frames, leading to inflated hit counts.

-  **Solutions:**

- Various datasets used along with hyperparameter tuning to improve accuracy as much as possible.

- Instead of only relying on object detection, we also implemented a collision detection algorithm that detects collision.

- Implementation of cooldown frames to improve accuracy and remove multiple detection of punches in consecutive frames.

## Results and Demo

- The live video tracking was successfully able to detect the boxing glove in frame.
- The project successfully detected the total number of hits in boxing and training videos. The implemented collision detection approach significantly improved the accuracy compared to the initial object detection method alone.
![Boxing Bag Detected](https://imgur.com/a/7hnZyf5)
![Boxing Detected](https://imgur.com/a/H0d1U6c)
- Link to the detected videos with bounding boxes: [Link](https://drive.google.com/file/d/1seuh84c9eUNC7D5we3DEl3DEJopxqmut/view?usp=sharing)

  

## References


- Data and models were sourced from Roboflow Universe: [Project Boxing](https://universe.roboflow.com/goodgoose/project-boxing-qwxns), [Boxing Gloves Detection](https://universe.roboflow.com/boxing-uuhxl/boxing-gloves-detection),[Boxing Gloves Detection Computer Vision Project](https://universe.roboflow.com/boxing-uuhxl/boxing-gloves-detection),[Boxing club Computer Vision Project](https://universe.roboflow.com/ie/boxing-club),[Boxing Detected](https://universe.roboflow.com/computer-vision-jrnie/boxing-detected)

- Videos for testing this from this google drive: [Link](https://www.google.com/url?q=https%3A%2F%2Fdrive.google.com%2Fdrive%2Ffolders%2F1UwZPZ7sqkmQrqbCP1ypquv2UHWkk0bj-) The above google drive is from the following punch classification project on github [link](https://github.com/balezz/Punch_DL?tab=readme-ov-file).
- Sparring video: [Link](https://www.youtube.com/watch?v=ZR0Spt7HKVc&t=28s)
- YOLOv8 https://github.com/ultralytics/ultralytics
