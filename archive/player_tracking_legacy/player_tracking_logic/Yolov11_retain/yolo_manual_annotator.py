import os
import cv2
from typing import List, Tuple

# =========================
# Config
# =========================
IMAGE_DIR = "data/frames"
LABEL_DIR = "data/labels"

CLASS_NAMES = {
    0: "CAR",
    1: "GCS",
    2: "REF",
}

VALID_EXTS = (".jpg", ".jpeg", ".png", ".bmp")

# Set the start frame here:
# 0 = start from the first image
# 1 = start from the second image
# 100 = start from the 101st image
# sri - 0-139
# ethan - 140-239
# nikhil - 240-339
# nithin - 340-439
# vinuk - 440-539
START_FRAME_INDEX = 140

os.makedirs(LABEL_DIR, exist_ok=True)

# =========================
# Global State
# =========================
drawing = False
start_point = (-1, -1)
end_point = (-1, -1)

cursor_x = -1
cursor_y = -1

# Each box: (class_id, x1, y1, x2, y2)
boxes: List[Tuple[int, int, int, int, int]] = []

current_class = 0
selected_box_idx = -1

current_image = None
display_image = None
image_w = 0
image_h = 0


def get_color(class_id: int):
    if class_id == 0:
        return (0, 0, 0)        # black
    if class_id == 1:
        return (0, 0, 255)      # red
    return (0, 255, 255)        # yellow


def clamp_box(x1: int, y1: int, x2: int, y2: int, w: int, h: int):
    x1 = max(0, min(x1, w - 1))
    x2 = max(0, min(x2, w - 1))
    y1 = max(0, min(y1, h - 1))
    y2 = max(0, min(y2, h - 1))
    return x1, y1, x2, y2


def normalize_box(x1: int, y1: int, x2: int, y2: int, w: int, h: int):
    x_min = min(x1, x2)
    x_max = max(x1, x2)
    y_min = min(y1, y2)
    y_max = max(y1, y2)

    bw = x_max - x_min
    bh = y_max - y_min
    xc = x_min + bw / 2.0
    yc = y_min + bh / 2.0

    return xc / w, yc / h, bw / w, bh / h


def save_labels(label_path: str):
    with open(label_path, "w", encoding="utf-8") as f:
        for class_id, x1, y1, x2, y2 in boxes:
            xc, yc, bw, bh = normalize_box(x1, y1, x2, y2, image_w, image_h)
            if bw <= 0 or bh <= 0:
                continue
            f.write(f"{class_id} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")


def load_labels(label_path: str):
    loaded = []
    if not os.path.exists(label_path):
        return loaded

    with open(label_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue

            class_id = int(parts[0])
            xc, yc, bw, bh = map(float, parts[1:])

            x_center = xc * image_w
            y_center = yc * image_h
            box_w = bw * image_w
            box_h = bh * image_h

            x1 = int(x_center - box_w / 2)
            y1 = int(y_center - box_h / 2)
            x2 = int(x_center + box_w / 2)
            y2 = int(y_center + box_h / 2)

            x1, y1, x2, y2 = clamp_box(x1, y1, x2, y2, image_w, image_h)
            loaded.append((class_id, x1, y1, x2, y2))

    return loaded


def point_inside_box(x, y, box):
    _, x1, y1, x2, y2 = box
    left = min(x1, x2)
    right = max(x1, x2)
    top = min(y1, y2)
    bottom = max(y1, y2)
    return left <= x <= right and top <= y <= bottom


def find_box_at_point(x, y):
    # Search from back to front, prioritising the most recently drawn box
    for i in range(len(boxes) - 1, -1, -1):
        if point_inside_box(x, y, boxes[i]):
            return i
    return -1


def redraw(image_name: str, img_index: int, total_images: int):
    global display_image
    display_image = current_image.copy()

    # Crosshair guide lines
    if 0 <= cursor_x < image_w and 0 <= cursor_y < image_h:
        guide_color = (180, 180, 180)
        cv2.line(display_image, (cursor_x, 0), (cursor_x, image_h - 1), guide_color, 1)
        cv2.line(display_image, (0, cursor_y), (image_w - 1, cursor_y), guide_color, 1)

        coord_text = f"({cursor_x}, {cursor_y})"
        text_x = min(cursor_x + 10, image_w - 140)
        text_y = max(cursor_y - 10, 20)
        cv2.putText(
            display_image,
            coord_text,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
            cv2.LINE_AA,
        )

    # Draw boxes
    for i, (class_id, x1, y1, x2, y2) in enumerate(boxes):
        color = get_color(class_id)
        thickness = 2

        if i == selected_box_idx:
            # Highlight the selected box
            cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.rectangle(display_image, (x1, y1), (x2, y2), color, 1)
        else:
            cv2.rectangle(display_image, (x1, y1), (x2, y2), color, thickness)

        cv2.putText(
            display_image,
            CLASS_NAMES[class_id],
            (x1, max(20, y1 - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
            cv2.LINE_AA,
        )

    # Preview of the box currently being dragged
    if drawing:
        color = get_color(current_class)
        cv2.rectangle(display_image, start_point, end_point, color, 1)

    info1 = f"[{img_index + 1}/{total_images}] {image_name}"
    selected_text = "None" if selected_box_idx < 0 else f"{selected_box_idx}"
    info2 = f"Current Class: {current_class} ({CLASS_NAMES[current_class]}) | Selected Box: {selected_text}"

    cv2.putText(display_image, info1, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
    cv2.putText(display_image, info2, (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

    # Shortcut key legend (top-right corner)
    overlay = display_image.copy()
    cv2.rectangle(overlay, (image_w - 320, 10), (image_w - 10, 240), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.40, display_image, 0.60, 0, display_image)

    shortcut_lines = [
        "Controls:",
        "Left drag = new box",
        "Right click = select box",
        "1/2/3 = class / relabel selected",
        "x = delete selected",
        "u = undo last added",
        "s = save",
        "d = next",
        "a = prev",
        "q = quit"
    ]

    x_offset = image_w - 305
    y_offset = 30
    for i, line in enumerate(shortcut_lines):
        cv2.putText(
            display_image,
            line,
            (x_offset, y_offset + i * 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )


def mouse_callback(event, x, y, flags, param):
    global drawing, start_point, end_point, boxes, cursor_x, cursor_y, selected_box_idx

    image_name, img_index, total_images = param
    cursor_x, cursor_y = x, y

    if event == cv2.EVENT_LBUTTONDOWN:
        selected_box_idx = -1
        drawing = True
        start_point = (x, y)
        end_point = (x, y)
        redraw(image_name, img_index, total_images)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (x, y)
        redraw(image_name, img_index, total_images)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)

        x1, y1 = start_point
        x2, y2 = end_point
        x1, y1, x2, y2 = clamp_box(x1, y1, x2, y2, image_w, image_h)

        if abs(x2 - x1) > 5 and abs(y2 - y1) > 5:
            boxes.append((current_class, x1, y1, x2, y2))
            selected_box_idx = len(boxes) - 1

        redraw(image_name, img_index, total_images)

    elif event == cv2.EVENT_RBUTTONDOWN:
        selected_box_idx = find_box_at_point(x, y)
        redraw(image_name, img_index, total_images)


def main():
    global current_image, display_image, boxes, current_class, image_w, image_h
    global cursor_x, cursor_y, selected_box_idx

    image_files = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(VALID_EXTS)])
    if not image_files:
        print(f"No images found in: {IMAGE_DIR}")
        return

    if START_FRAME_INDEX < 0 or START_FRAME_INDEX >= len(image_files):
        print(f"Invalid START_FRAME_INDEX: {START_FRAME_INDEX}")
        print(f"It must be between 0 and {len(image_files) - 1}")
        return

    idx = START_FRAME_INDEX
    window_name = "YOLO Manual Annotator"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while 0 <= idx < len(image_files):
        image_name = image_files[idx]
        image_path = os.path.join(IMAGE_DIR, image_name)
        label_name = os.path.splitext(image_name)[0] + ".txt"
        label_path = os.path.join(LABEL_DIR, label_name)

        current_image = cv2.imread(image_path)
        if current_image is None:
            print(f"Failed to load image: {image_path}")
            idx += 1
            continue

        image_h, image_w = current_image.shape[:2]
        boxes = load_labels(label_path)

        cursor_x = image_w // 2
        cursor_y = image_h // 2
        selected_box_idx = -1

        redraw(image_name, idx, len(image_files))
        cv2.setMouseCallback(window_name, mouse_callback, param=(image_name, idx, len(image_files)))

        while True:
            cv2.imshow(window_name, display_image)
            key = cv2.waitKey(20) & 0xFF

            if key in [ord("1"), ord("2"), ord("3")]:
                new_class = int(chr(key)) - 1
                if selected_box_idx >= 0:
                    _, x1, y1, x2, y2 = boxes[selected_box_idx]
                    boxes[selected_box_idx] = (new_class, x1, y1, x2, y2)
                else:
                    current_class = new_class
                redraw(image_name, idx, len(image_files))

            elif key == ord("x"):
                if selected_box_idx >= 0:
                    boxes.pop(selected_box_idx)
                    selected_box_idx = -1
                    redraw(image_name, idx, len(image_files))

            elif key == ord("u"):
                if boxes:
                    boxes.pop()
                    selected_box_idx = -1
                    redraw(image_name, idx, len(image_files))

            elif key == ord("s"):
                save_labels(label_path)
                print(f"Saved: {label_path}")
                redraw(image_name, idx, len(image_files))

            elif key == ord("d"):
                save_labels(label_path)
                print(f"Saved and next: {label_path}")
                idx += 1
                break

            elif key == ord("a"):
                save_labels(label_path)
                print(f"Saved and previous: {label_path}")
                idx = max(0, idx - 1)
                break

            elif key == ord("q"):
                save_labels(label_path)
                print(f"Saved and quit: {label_path}")
                cv2.destroyAllWindows()
                return

    cv2.destroyAllWindows()
    print("Annotation finished.")


if __name__ == "__main__":
    main()