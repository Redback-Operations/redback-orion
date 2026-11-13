import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import logging
import sys
import os
from contextlib import redirect_stdout

# Suppress all output to terminal
sys.stdout = open(os.devnull, 'w')

# Set up logging to suppress debug information (if applicable)
logging.getLogger('ultralytics').setLevel(logging.ERROR)

# Load the YOLO model
model = YOLO('yolov8n.pt')  # Make sure you have the YOLO model file available

# Reset stdout to default after setting up the model
sys.stdout = sys.__stdout__

# Streamlit app title
st.title("Player Tracking with YOLO")

# File uploader widget
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi"])

# Process the video if a file is uploaded
if uploaded_file is not None:
    # Save the uploaded video to a temporary file
    temp_video_path = "temp_video.mp4"
    with open(temp_video_path, "wb") as f:
        f.write(uploaded_file.read())

    # Open the video
    cap = cv2.VideoCapture(temp_video_path)

    if not cap.isOpened():
        st.error("Error: Could not open video.")
    else:
        st.write("Video processing started...")

        # Display video frames
        frame_window = st.empty()  # Placeholder for video display
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Run YOLO detection on the frame
            results = model(frame)

            # Annotate the frame
            if results:
                frame = results[0].plot()  # Annotated frame

            # Convert the frame to RGB for Streamlit
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Display the frame
            frame_window.image(frame, channels="RGB", use_container_width=True)

            # Stop if user closes the app or video ends
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        st.write("Video processing complete.")
