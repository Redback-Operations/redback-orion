# Face Detection API Documentation

## Overview
This project provides an API for face detection and facial feature extraction using a combination of YOLOv3 and Dlib models. The API accepts video frames as input and returns JSON data containing information about detected faces, including bounding boxes, confidence scores, facial landmarks, and face embeddings.

## Project Structure
1) **app.py** 
2) **video_processing.py**
3) **models.py** 
4) **config.py**
5) **yolov3-wider_16000.weights**
6) **yolov3-face.cfg**
7) **shape_predictor_68_face_landmarks.dat**
8) **dlib_face_recognition_resnet_model_v1.dat**
9) **crowd.mp4**

## 1) app.py
The **app.py** file contains the FastAPI application, which provides an endpoint to process an image frame and return the face detection results in JSON format.

#### Functions:
1) **process_frame**: This is the main API endpoint that accepts an uploaded image file. The image is processed to detect faces, and facial features are extracted. The results are returned as a JSON response.

```
@app.post("/process_frame/")
async def process_frame(file: UploadFile = File(...)):
    # Implementation details...
    return JSONResponse(content=frame_data)
```
#### Usage:
Run the FastAPI application using:

`uvicorn app:app --reload`

Send a POST request with an image file to the /process_frame/ endpoint to get the face detection results.

***Use main.py as a reference to understand how the endpoint is called.***

## 2) video_processing.py
The **video_processing.py** file provides functionality to process video files and detect faces in each frame. This script can be used independently or integrated into other applications to process video data.

#### Functions:
1) **process_video:** Processes a video file and detects faces in selected frames (3 frames per second). The detected faces' information is printed in JSON format.
   ```
   def process_video(video_path, net, output_layers, shape_predictor, face_rec_model):
    # Implementation details...
    ```
## 3) models.py
The **models.py** file contains the model loading and face detection functions. It includes functions to load YOLOv3 and Dlib models and to detect faces and extract facial characteristics.

#### Functions:
1) **load_yolo_model:** Loads the YOLOv3 model using the specified weights and configuration files.
   ```
   def load_yolo_model(weights_path, config_path):
    # Implementation details...
    ```
2) **detect_faces:** Detects faces in an image using the YOLOv3 model.
   ```
    def detect_faces(img, net, output_layers, confidence_threshold=0.5):
    # Implementation details...
   ```

3) **extract_face_characteristics:** Extracts facial landmarks and embeddings using the Dlib model.
   ```
    def extract_face_characteristics(img, faces, shape_predictor, face_rec_model):
    # Implementation details...
   ```


## 4) config.py
The **config.py** file contains configuration settings for the paths to the model files, video files, and API URL.

#### Variables:
1) **weights_path:** Path to the YOLOv3 weights file.
2) **config_path:** Path to the YOLOv3 configuration file.
3) **video_path:** Path to the video file for processing.
4) **image_path:** Path to the image file.
5) **api_url:** URL of the FastAPI endpoint for processing frames.
6) **shape_predictor_path:** Path to the Dlib shape predictor model.
7) **face_rec_model_path:** Path to the Dlib face recognition model.

## 5) Model Files
1) **yolov3-wider_16000.weights:** YOLOv3 model weights for face detection.
2) **yolov3-face.cfg:** YOLOv3 configuration file for face detection.
3) **shape_predictor_68_face_landmarks.dat:** Dlib model for predicting 68 facial landmarks.
4) **dlib_face_recognition_resnet_model_v1.dat:** Dlib ResNet model for face recognition. 

## Installation
#### Prerequisites
1) Python 3.7+
2) FastAPI
3) OpenCV
4) Dlib

## Setup
1) Clone the repository and navigate to the project directory.
2) Place the model files **(yolov3-wider_16000.weights, yolov3-face.cfg, shape_predictor_68_face_landmarks.dat, dlib_face_recognition_resnet_model_v1.dat)** in the project directory.

## Running the Application
1) #### Start the FastAPI server:
   ```
   uvicorn app:app --reload
   ```
2) #### Send a POST request to the **/process_frame/** endpoint:
   Use a tool like **curl**, **Postman**, or any **HTTP** client to send an image file to the API:

   ```
   curl -X POST "http://127.0.0.1:8000/process_frame/" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@path_to_image.jpg"
   ```
   ***Use main.py as a reference to understand how the endpoint is called.***

## Example Output
The API will return a JSON response with the following structure:
```
{
    "face_count": 2,
    "faces": [
        {
            "face_id": 0,
            "bbox": [150, 120, 50, 60],
            "confidence": 0.85,
            "landmarks": [[30, 40], [32, 45], [28, 43]],
            "embedding": [...]
        },
        {
            "face_id": 1,
            "bbox": [300, 200, 50, 60],
            "confidence": 0.88,
            "landmarks": [[35, 50], [37, 55], [33, 53]],
            "embedding": [...]
        }
    ]
}
```

## Future Work
1) **Documentation:** Comprehensive documentation of the code, models, and APIs.
2) **Scalability:** Implement Kafka for queuing frames and processing them in parallel to improve processing speed.
3) **Database Integration:** Add MongoDB to store JSON outputs for better data management and retrieval.
4) **Testing:** Extensive testing and optimization for real-time video processing.
5) **Deployment:** Deployment of the API on a cloud platform for scalability and accessibility.

## Acknowledgments
1) YOLOv3 for face detection.
2) Dlib for facial landmark detection and face recognition.

## Participants
### Member 1: Mustafa Tariq (223124219)
1) Tested YOLOv3 for face detection and opted YOLOv3 to be most suitable modle for face detection.
2) Developed the YOLOv3 model integration for face detection.
3) Ran some tests through videos and pictures to test the accuracy of the face detection model.
4) Implemented the FastAPI backend for processing image frames.
5) Worked on optimizing the Dlib model for facial landmark detection.
6) Managed the video processing module, ensuring accurate frame extraction and processing.
7) Tested database (MongoDB) integration by pushing the json response to a database document. It was not part of this project, but it was for the sake of understanding of how the database would be integrated to the module.

### Member 2: Abdul Ahad (223735551)
1) Helped in research for the best possible model for face detection.
2) Implemented and tested Haar Cascade model for face detection.
3) Handled the face embedding generation using Dlib's ResNet model.
4) Contributed to the JSON response structure, ensuring clear and detailed data output.
5) Assisted with testing and debugging the entire application.
6) Worked on the configuration management, making sure all paths and settings were correctly implemented.