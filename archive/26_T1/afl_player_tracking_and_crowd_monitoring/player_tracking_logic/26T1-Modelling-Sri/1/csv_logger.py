import csv
import os


def create_csv_file(csv_path): # Create a CSV file with the specified path and write the header row for tracking results
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "frame",
            "track_id",
            "class_name",
            "confidence",
            "x1",
            "y1",
            "x2",
            "y2",
            "cx",
            "cy"
        ])


def append_result_to_csv(csv_path, frame_number, result): # Append tracking results for a given frame to the CSV file, including frame number, track ID, class name, confidence, bounding box coordinates, and center coordinates
    if result.boxes is None:
        return

    names = result.names

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)

        for box in result.boxes:
            if box.id is None:
                continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            track_id = int(box.id[0])

            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            class_name = names[cls_id]

            writer.writerow([
                frame_number,
                track_id,
                class_name,
                conf,
                x1,
                y1,
                x2,
                y2,
                cx,
                cy
            ])