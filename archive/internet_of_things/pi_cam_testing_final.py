from flask import Flask, Response, make_response, abort
import cv2
import os
import ssl
from io import BytesIO
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()

# Set up users
users = {
    "user": generate_password_hash(os.getenv("USER_PASSWORD", "default_password"))
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

def generate_frames():
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not camera.isOpened():
        abort(500, "Failed to open camera")
    
    try:
        while True:
            success, frame = camera.read()
            if not success:
                print("Failed to capture frame from camera. Check camera initialization and settings.")
                break

            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                print("Failed to encode the frame into JPEG. Continuing...")
                continue

            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        camera.release()
        print("Camera has been released.")

@app.route('/video_feed')
@auth.login_required
def video_feed():
    response = make_response(Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame'))
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

if __name__ == '__main__':
    # Generate a self-signed SSL certificate if you haven't already done so.
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    app.run(host='0.0.0.0', port=5000, threaded=True, ssl_context=ssl_context) # nosec
