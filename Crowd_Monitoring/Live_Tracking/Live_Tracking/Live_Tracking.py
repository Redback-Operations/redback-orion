from flask import Flask, Response
import cv2
import numpy as np
from ultralytics import YOLO
from pymongo import MongoClient
from datetime import datetime, date
import threading
from flask_cors import CORS
import os


app = Flask(__name__)
CORS(app)

# Load YOLO model
model = YOLO('yolov8n.pt')  # or use a different YOLO version

# RTSP stream URL
# Retrive the RTSP stream URL from iSpy or Wireshark
# Replace the rtsp_url with your own RTSP stream URL
rtsp_url = ''
''' 
# MongoDB connection
client = MongoClient('')
db = client["CrowdTracking"]
collection = db["Crowd"]
''' 
frame_id = 0
current_date = date.today()

global_frame = None
global_result = None
def generate_frames():
    global frame_id, current_date, global_frame, global_result
    cap = cv2.VideoCapture(rtsp_url)
    while True:
        now = datetime.now()
        # Read the frame from the stream
        # If the frame was not read, then break the loop and print an error
        ret, frame = cap.read()
        if not ret:
            print('Error reading the frame')
            break

        # Perform YOLO detection
        results = model(frame)

        # Process results with box coordinates and confidence scores
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = box.conf[0]
                cls = int(box.cls[0])
            
                if cls == 0:  # Assuming class 0 is person
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f'Person: {conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
             
        # Save the number of persons detected to MongoDB
        # Save the frame_id, timestamp and the total number of persons detected
        data = {
            
            "frame_id": frame_id,
            "timestamp": now.strftime("%d/%m/%Y %H:%M:%S"),
            "total_persons": len(boxes)
        }
        collection.insert_one(data)

        # Delete the old data from MongoDB when entering a new day
        # if the current date is greater than the date of the last frame
        # then reset the frame_id and delete all the data from the collection
        if now.date() > current_date:
            frame_id = 0
            current_date = now.date()
            collection.delete_many({})
            print (f"Data will be resetted for new day: {current_date}")

        # Display the number of persons detected on the frame       
        cv2.rectangle(frame, (10, 10), (310, 60), (255, 255, 255), -1)
        cv2.putText(frame, f'Total Persons: {len(boxes)}', (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        frame_id += 1

        global_frame = frame
        global_result = len(boxes)

        # Encode the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
# Route the display the video feed
# The video feed will be displayed on the web browser
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    threading.Thread(target=generate_frames, daemon=True).start()
    app.run(port=8000) #nosec

