from flask import Flask, Response, jsonify, request
import cv2
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize the Flask-Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"]
)

# Initialize video capture with OpenCV.
cap = cv2.VideoCapture(0)


def generate_frames():
    try:
        while True:
            success, frame = cap.read()  # Read the camera frame
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    logging.error("Failed to encode frame")
                    continue
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\r')  # Concatenate video frame data
    except Exception as e:
        logging.exception("Error in generating video frames")
        raise


@app.route('/video')
@limiter.limit("10 per minute")
def video():
    try:
        # Return the response generated along with the specific media
        # type (mime type).
        return Response(generate_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        logging.exception("Error in /video route")
        return jsonify(error=str(e)), 500


@app.route('/validate_input', methods=['GET'])
def validate_input():
    user_input = request.args.get('input', '')
    if not re.match("^[a-zA-Z0-9_]*$", user_input):
        return jsonify(error="Invalid input"), 400
    return jsonify(message="Valid input", input=user_input), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify(error="Resource not found"), 404


@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify(error="Rate limit exceeded"), 429


@app.errorhandler(500)
def internal_error(error):
    return jsonify(error="Internal server error"), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) #nosec
