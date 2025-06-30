from flask import Flask, request, render_template, redirect, url_for, Response
import cv2 as cv
import numpy as np
import os

# Initialize Flask app
app = Flask(__name__)

# Load the pre-trained neural network model
net = cv.dnn.readNetFromTensorflow("Pose_Estimation/graph_opt.pb")

# Set the input size for the network
inWidth = 368
inHeight = 368
thr = 0.2

# Define the BODY_PARTS with names as keys
BODY_PARTS = {
    "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
    "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
    "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
    "LEye": 15, "REar": 16, "LEar": 17, "Background": 18
}

POSE_PAIRS = [
    ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
    ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
    ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
    ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
    ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"]
]

def pose_estimation(frame):
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    net.setInput(cv.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight), (127.5, 127.5, 127.5), swapRB=True, crop=False))
    out = net.forward()
    out = out[:, :19, :, :]

    assert(len(BODY_PARTS) == out.shape[1])

    points = []

    for i in range(len(BODY_PARTS)):
        heatMap = out[0, i, :, :]
        _, conf, _, point = cv.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / out.shape[3]
        y = (frameHeight * point[1]) / out.shape[2]

        points.append((int(x), int(y)) if conf > thr else None)

    # Draw skeleton overlay
    for pair in POSE_PAIRS:
        partFrom = pair[0]
        partTo = pair[1]
        idFrom = BODY_PARTS[partFrom]
        idTo = BODY_PARTS[partTo]

        if points[idFrom] and points[idTo]:
            cv.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
            cv.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
            cv.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)

    return frame, points  # Return the processed image frame and keypoints

def pose_estimation_camera(frame):
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    net.setInput(cv.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight), (127.5, 127.5, 127.5), swapRB=True, crop=False))
    out = net.forward()
    out = out[:, :19, :, :]

    assert(len(BODY_PARTS) == out.shape[1])

    points = []

    for i in range(len(BODY_PARTS)):
        heatMap = out[0, i, :, :]
        _, conf, _, point = cv.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / out.shape[3]
        y = (frameHeight * point[1]) / out.shape[2]

        points.append((int(x), int(y)) if conf > thr else None)

    return points  # Return the keypoints

def euclidean_distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))

def calculate_similarity_percentage(keypoints1, keypoints2, max_distance=200):
    if len(keypoints1) != len(keypoints2):
        raise ValueError("Keypoints from both images must have the same length.")
    
    total_distance = 0
    valid_points = 0

    for kp1, kp2 in zip(keypoints1, keypoints2):
        if kp1 is not None and kp2 is not None:
            distance = euclidean_distance(kp1, kp2)
            if distance < max_distance:  # Consider only valid distances
                total_distance += distance
                valid_points += 1

    if valid_points == 0:
        return 0

    average_distance = total_distance / valid_points
    similarity_percentage = max(0, 100 * (1 - average_distance / max_distance))
    
    return similarity_percentage

def gen_frames():
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Use the separate pose_estimation function for webcam frames
        frame_with_skeleton, _ = pose_estimation(frame)
        _, buffer = cv.imencode('.jpg', frame_with_skeleton)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera_feed')
def camera_feed():
    return render_template('camera_feed.html')

@app.route('/pose_matching')
def pose_matching():
    return render_template('pose_matching.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'file1' not in request.files or 'file2' not in request.files:
        return redirect(url_for('pose_matching'))

    file1 = request.files['file1']
    file2 = request.files['file2']

    if file1.filename == '' or file2.filename == '':
        return redirect(url_for('pose_matching'))

    if file1 and file2:
        img1 = cv.imdecode(np.frombuffer(file1.read(), np.uint8), cv.IMREAD_COLOR)
        img2 = cv.imdecode(np.frombuffer(file2.read(), np.uint8), cv.IMREAD_COLOR)

        img1, keypoints_img1 = pose_estimation(img1)
        img2, keypoints_img2 = pose_estimation(img2)

        # Ensure keypoints are extracted correctly and have the same length
        if len(keypoints_img1) != len(keypoints_img2):
            return redirect(url_for('pose_matching'))

        similarity_percentage = calculate_similarity_percentage(keypoints_img1, keypoints_img2)

        img1_path = 'static/uploads/temp_img1.jpg'
        img2_path = 'static/uploads/temp_img2.jpg'
        cv.imwrite(img1_path, img1)
        cv.imwrite(img2_path, img2)

        return render_template('pose_matching.html', similarity=f'{similarity_percentage:.2f}%', img1_path=img1_path, img2_path=img2_path)

    else:
        return redirect(url_for('pose_matching'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset():
    if os.path.exists('static/uploads/temp_img1.jpg'):
        os.remove('static/uploads/temp_img1.jpg')
    if os.path.exists('static/uploads/temp_img2.jpg'):
        os.remove('static/uploads/temp_img2.jpg')
    return redirect(url_for('pose_matching'))

if __name__ == '__main__':
    app.run()
