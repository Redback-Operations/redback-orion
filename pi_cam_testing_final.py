from flask import Flask, Response
import cv2

app = Flask(__name__)

def generate_frames():
    # Initialize the camera
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Using V4L2 to capture from the camera.
    if not camera.isOpened():
        raise RuntimeError("Cannot open camera")
    
    try:
        while True:
            # Capture frame-by-frame
            success, frame = camera.read()
            if not success:
                print("Failed to capture frame from camera. Check camera initialization and settings.")
                break

            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                print("Failed to encode the frame into JPEG. Continuing...")
                continue  # Skip this frame

            # Convert to bytes and yield
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        # Release the camera when done
        camera.release()
        print("Camera has been released.")

@app.route('/video_feed')
def video_feed():
    # This route returns the streaming response using the generator function
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, threaded=True)
