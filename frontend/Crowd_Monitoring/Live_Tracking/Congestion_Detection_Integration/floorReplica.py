import cv2
import numpy as np

def floorReplica(canvasHeight, canvasWidth, tilesX, tilesY, rtspUrl):
    # Create a VideoCapture object
    cap = cv2.VideoCapture(rtspUrl)

    # Check if camera opened successfully
    success, frame = cap.read()
    if not success:
        cap.release()
        cap = cv2.VideoCapture(rtspUrl)
        success, frame = cap.read()
        if not success:
            raise Exception("Failed to read video stream - floorReplica.py")
    
    tileHeight = canvasHeight // tilesY
    tileWidth = canvasWidth // tilesX

    floorImage = np.ones((canvasHeight, canvasWidth, 3), dtype=np.uint8) * 255

    for y in range(0, canvasHeight, tileHeight):
        for x in range(0, canvasWidth, tileWidth):
            cv2.rectangle(floorImage, (x, y), (x + tileWidth, y + tileHeight), (0, 0, 0), 1)
    return floorImage