import cv2
import requests
import numpy as np
import config
from matplotlib import pyplot as plt
import json

def video_processing(video_path, url):
    # URL of the FastAPI endpoint
    api_url = url
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)  # Get the frames per second of the video
    interval = int(fps / 3)  # Interval for extracting 3 frames per second
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of video
        
        if frame_count % interval == 0:
            # Encode frame as JPEG
            _, img_encoded = cv2.imencode('.jpg', frame)
            img_bytes = img_encoded.tobytes()
            
            # Prepare file for API request
            files = {'file': ('frame.jpg', img_bytes, 'image/jpeg')}
            
            # Send POST request to API
            response = requests.post(api_url, files=files)
            print(f"Response: {response.json()}")
        
        frame_count += 1
    
    cap.release()


def image_processing(image_path, url):
    api_url = url
    
    # Read and process the image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not read image.")
        return
    
    _, img_encoded = cv2.imencode('.jpg', image)
    img_bytes = img_encoded.tobytes()
    
    files = {'file': ('image.jpg', img_bytes, 'image/jpeg')}
    
    response = requests.post(api_url, files=files)
    result = response.json()
    
    # Display the image with bounding boxes
    if 'faces' in result:
        for face in result['faces']:
            # Draw bounding box around the face
            x, y, w, h = face['bbox']
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw facial landmarks
            for (lx, ly) in face['landmarks']:
                cv2.circle(image, (x + lx, y + ly), 2, (0, 0, 255), -1)  # Red dots for landmarks
    
    # Convert BGR image to RGB for displaying with matplotlib
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Display image with bounding boxes and landmarks
    plt.imshow(image_rgb)
    plt.axis('off')
    plt.show()
    
    return result


if __name__ == "__main__":
    #video_processing(config.video_path, config.)
    # Process single image
    result = image_processing(config.image_path, config.api_url)
    # Print the result in a formatted way
    if isinstance(result, dict) or isinstance(result, list):
        print(json.dumps(result, indent=4))
    else:
        print(result)