import io
import picamera
from flask import Flask, Response

app = Flask(__name__)

def generate_frames():
    # Create a camera object using the PiCamera library, setting up the camera's properties.
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)  # Set the camera resolution.
        camera.framerate = 24  # Set the camera framerate.
        stream = io.BytesIO()  # Create an in-memory stream to hold image data.
        
        # Continuously capture images from the camera as jpeg and write to the stream.
        for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            stream.seek(0)  # Move to the beginning of the stream to read the image data.
            # Yield a properly formatted multipart response with the jpeg image data.
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n'
            stream.seek(0)  # Reset the stream position to the start.
            stream.truncate()  # Clear the stream to prepare for the next frame.
            
@app.route('/video_feed')
def video_feed():
    # Create an HTTP response that streams the jpeg frames using the multipart replace header.
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Start the Flask application on all interfaces at port 5000 with threading enabled.
    app.run(host='0.0.0.0', port=5000, threaded=True) # nosec
