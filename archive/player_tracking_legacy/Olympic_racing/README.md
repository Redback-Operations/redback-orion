---
sidebar_position: 1
---
# Pose Detection and Segmentation on Olympic Racing Video using YOLOv11-Pose & SAM2
![readme style: standard](https://img.shields.io/badge/readme%20style-standard-brightgreen)
![Roboflow](https://img.shields.io/badge/Roboflow-Model%20Status-blue)
![Python](https://img.shields.io/badge/Python-3.12-blue)

## Overview
In this project, we leverage YOLOv11-Pose, a cutting-edge real-time pose estimation model, to detect and track body keypoints of sprinters in Olympic racing videos. We enhance this by using SAM2 to segment specific regions of athletes, enabling advanced visual analysis like joint-region overlays, bounding masks, and spatial tracking.

## Models Used
## 1. YOLOv11-Pose
   
  -YOLOv11 is the next-gen version of the YOLO (You Only Look Once) object detection family, optimized for pose estimation tasks.

  -YOLOv11-Pose extends this by predicting keypoints (e.g., shoulders, elbows, knees, ankles) in addition to bounding boxes.

  -Fast and lightweight, suitable for real-time inference.

Output:

  -17 Keypoints per person (COCO format)
  
  -Confidence scores
  
  -Pose lines between joints

## 2. SAM2 (Segment Anything v2)
   
  -Developed by Meta AI, SAM2 is a foundation model for image segmentation.

  -Segments anything in an image — no training or bounding boxes needed.



## Model in Action

 Below is a video showing our model in action, demonstrating its ability to accurately detect and track atheletes : 
 
  [Trained model deployed on 1080p video](https://drive.google.com/file/d/1UXzxKwwMym1JCM7lY5Y5c-fxMjrZk8Xc/view?usp=drive_link)
  
  Some screenshots showcasing the output : 
  
  ![image](https://github.com/user-attachments/assets/51270617-4345-4ec5-94f2-2f3813258384)


## Installation

### Prerequisites
- NumPy
- Matplotlib
- Ultralytics
-SAM2

Dependencies installed with ultralytics: torch, torchvision
opencv-python
numpy, pandas, matplotlib, scipy, seaborn
pyyaml, requests, tqdm, pillow


### Steps
1. **Clone the Repository:**
    ```bash
    https://github.com/plasma141/redback-orion
    ```
2. **Run the Project on Google Colab:**
   - We have provided a Google Colab notebook that sets up everything you need. Click the link below to open the notebook and follow the instructions to run the project:

   - [Run on Google Colab](annotate-train-deploy_train.ipynb)
     
      
4. **Setup YOLOv11_pose:**
   - Follow the [YOLOv8 installation guide](https://docs.ultralytics.com/models/yolov8/) to set up the detection model.

5. **Run inference on Olympic video:**
    - Use the following command to run the detection model:
    ```bash
    results = model('olympic_race.mp4', show=True)
    ```


## Contributing
Contributions are welcome! Please follow the standard contribution guidelines:

1. Fork the repository from [GitHub](https://github.com/plasma141/redback-orion).
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.



## Data Collection
All data was collected off broadcast tv in Australia which is covered by the Australian Educational Licence which is held by Deakin University. Only data used by this collection method was used to train our model.
- [Screenrights](https://www.screenrights.org/screen-audiences/screenrights-licences/australian-educational-licences/)
- [Copyright](https://www.copyright.com.au/licences-permission/educational-licences/)

## Owner :sparkles:
- [*Mohitpreet Singh*](https://github.com/plasma141)


## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/Redback-Operations/redback-documentation/blob/main/LICENSE) file for details.

## Acknowledgements
We would like to extend our gratitude to the following:

- **YOLO and Ultralytics Communities:** Thank you for your contributions to the field of object detection and tracking. Your work has been instrumental in the development of our project.
- **Roboflow:** Special thanks for providing platform and annotation tools that have significantly contributed to the accuracy and efficiency of our model.
