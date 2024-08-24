from flask import Flask, jsonify, Response
from flask_cors import CORS
from cameraProcessing import CameraProcessing
from database import Database

app = Flask(__name__)
cors = CORS(app)
cameraProcessor = CameraProcessing()
db = Database()

@app.route("/api/peopleCount", methods=["GET"])
def getPeopleCount():
    count = db.getlastestRecord()
    return jsonify({"peopleCount": count})

@app.route("/api/videoFeed", methods=["GET"])
def videoFeed():
    return Response(cameraProcessor.getFrame(),
        mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/api/annotatedVideoFeed", methods=["GET"])
def annotatedVideoFeed():
    return Response(cameraProcessor.getAnnotatedFrame(),
        mimetype="multipart/x-mixed-replace; boundary=frame")
    
if __name__ == "__main__":
    app.run(debug=True, port=8000)