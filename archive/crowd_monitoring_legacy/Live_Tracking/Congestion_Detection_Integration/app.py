from flask import Flask, jsonify, Response, stream_with_context
from flask_cors import CORS
from cameraProcessing import CameraProcessor
from database import Database

app = Flask(__name__)
cors = CORS(app)
cameraProcessor = CameraProcessor()
db = Database()


# routes for people count
@app.route("/api/peopleCount", methods=["GET"])
def getPeopleCount():
    count = db.getlastestRecord()
    return jsonify({"peopleCount": count})


# routes for main camera display
@app.route("/LiveTracking/videoFeed", methods=["GET"])
def videoFeed():
    return Response(
        stream_with_context(cameraProcessor.getFrame()),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


# routes for annotated frame or 2d floor plan
@app.route("/LiveTracking/annotatedVideoFeed", methods=["GET"])
def annotatedVideoFeed():
    return Response(
        stream_with_context(cameraProcessor.getAnnotatedFrame()),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


if __name__ == "__main__":
    app.run(port=8000)
