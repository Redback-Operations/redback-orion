from flask import Flask, jsonify, Response, stream_with_context
from flask_cors import CORS
from cameraProcessing import CameraProcessor
from database import Database

# Configuration
# VIDEO_SOURCE = 0  # Default camera
# IS_VIDEO = False  # Set to True if using a video file
VIDEO_SOURCE = "/Users/apple/Desktop/Deakin/T2_2024/SIT764_Capstone/Crowd_Monitor/market-square.mp4"
IS_VIDEO = True

# Create Flask app
app = Flask(__name__)
cors = CORS(app)

# Initialize camera processor and database
camera_processor = CameraProcessor(source=VIDEO_SOURCE, is_video=IS_VIDEO)
#db = Database()

# Routes for people count
@app.route("/api/peopleCount", methods=["GET"])
def get_people_count():
    """Retrieve the latest people count"""
    count = db.getlastestRecord()
    return jsonify({"peopleCount": count})

# Routes for main camera display
@app.route("/LiveTracking/videoFeed", methods=["GET"])
def video_feed():
    """Stream raw video feed"""
    return Response(stream_with_context(camera_processor.get_frame()),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

# Routes for annotated frame or 2D floor plan
@app.route("/LiveTracking/annotatedVideoFeed", methods=["GET"])
def annotated_video_feed():
    """Stream annotated video feed"""
    return Response(stream_with_context(camera_processor.get_annotated_frame()),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    app.run(port=8000)