import json

def process_tracking_data(detections):
    processed = []

    try:
        for det in detections:
            player = {
                "id": getattr(det, "id", None),
                "bbox": getattr(det, "bbox", None),
                "confidence": getattr(det, "confidence", None)
            }
            processed.append(player)
    except:
        print("⚠️ Detection format unknown, using raw data")
        return detections

    return processed