from flask import Flask, Response
import cv2

app = Flask(__name__)

# Initialize video capture with OpenCV.
cap = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = cap.read()  # Read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Concatenate video frame data

@app.route('/video')
def video():
    # Return the response generated along with the specific media
    # type (mime type).
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
