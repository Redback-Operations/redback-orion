"""Interactive OpenCV tool for correcting YOLO labels manually."""

from pathlib import Path
from typing import List, Tuple
import cv2

from labelling_pipeline.utils import list_image_files


Box = Tuple[int, int, int, int, int]


class YoloManualAnnotator:
    """Manual YOLO annotation tool built around the original OpenCV workflow."""

    def __init__(self, config) -> None:
        self.config = config
        self.image_dir = Path(config.FRAME_DIR)
        self.label_dir = Path(config.LABEL_DIR)
        self.label_dir.mkdir(parents=True, exist_ok=True)

        self.drawing = False
        self.start_point = (-1, -1)
        self.end_point = (-1, -1)
        self.cursor_x = -1
        self.cursor_y = -1
        self.boxes: List[Box] = []
        self.current_class = 0
        self.selected_box_idx = -1
        self.current_image = None
        self.display_image = None
        self.image_w = 0
        self.image_h = 0

    def get_color(self, class_id: int):
        """Return the BGR drawing colour for a class id."""
        return self.config.CLASS_BOX_COLOURS.get(class_id, (255, 255, 255))

    @staticmethod
    def clamp_box(x1: int, y1: int, x2: int, y2: int, w: int, h: int):
        """Clamp a box to image boundaries."""
        x1 = max(0, min(x1, w - 1))
        x2 = max(0, min(x2, w - 1))
        y1 = max(0, min(y1, h - 1))
        y2 = max(0, min(y2, h - 1))
        return x1, y1, x2, y2

    @staticmethod
    def normalize_box(x1: int, y1: int, x2: int, y2: int, w: int, h: int):
        """Convert pixel xyxy coordinates into YOLO-normalised coordinates."""
        x_min = min(x1, x2)
        x_max = max(x1, x2)
        y_min = min(y1, y2)
        y_max = max(y1, y2)

        box_w = x_max - x_min
        box_h = y_max - y_min
        x_center = x_min + box_w / 2.0
        y_center = y_min + box_h / 2.0

        return x_center / w, y_center / h, box_w / w, box_h / h

    def save_labels(self, label_path: Path) -> None:
        """Save current boxes to a YOLO .txt file."""
        with open(label_path, "w", encoding="utf-8") as f:
            for class_id, x1, y1, x2, y2 in self.boxes:
                x_center, y_center, box_w, box_h = self.normalize_box(
                    x1, y1, x2, y2, self.image_w, self.image_h
                )
                if box_w <= 0 or box_h <= 0:
                    continue
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {box_w:.6f} {box_h:.6f}\n")

    def load_labels(self, label_path: Path) -> List[Box]:
        """Load YOLO labels for the current image and convert them to pixel boxes."""
        loaded: List[Box] = []
        if not label_path.exists():
            return loaded

        with open(label_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 5:
                    continue

                class_id = int(parts[0])
                x_center_norm, y_center_norm, width_norm, height_norm = map(float, parts[1:])

                x_center = x_center_norm * self.image_w
                y_center = y_center_norm * self.image_h
                box_w = width_norm * self.image_w
                box_h = height_norm * self.image_h

                x1 = int(x_center - box_w / 2)
                y1 = int(y_center - box_h / 2)
                x2 = int(x_center + box_w / 2)
                y2 = int(y_center + box_h / 2)

                x1, y1, x2, y2 = self.clamp_box(x1, y1, x2, y2, self.image_w, self.image_h)
                loaded.append((class_id, x1, y1, x2, y2))

        return loaded

    @staticmethod
    def point_inside_box(x: int, y: int, box: Box) -> bool:
        """Check whether a point is inside a box."""
        _, x1, y1, x2, y2 = box
        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)
        return left <= x <= right and top <= y <= bottom

    def find_box_at_point(self, x: int, y: int) -> int:
        """Find the latest drawn box at a mouse point."""
        for idx in range(len(self.boxes) - 1, -1, -1):
            if self.point_inside_box(x, y, self.boxes[idx]):
                return idx
        return -1

    def redraw(self, image_name: str, img_index: int, total_images: int) -> None:
        """Redraw the image, all boxes, and the keyboard shortcut overlay."""
        self.display_image = self.current_image.copy()

        if 0 <= self.cursor_x < self.image_w and 0 <= self.cursor_y < self.image_h:
            guide_color = (180, 180, 180)
            cv2.line(self.display_image, (self.cursor_x, 0), (self.cursor_x, self.image_h - 1), guide_color, 1)
            cv2.line(self.display_image, (0, self.cursor_y), (self.image_w - 1, self.cursor_y), guide_color, 1)

            coord_text = f"({self.cursor_x}, {self.cursor_y})"
            text_x = min(self.cursor_x + 10, self.image_w - 140)
            text_y = max(self.cursor_y - 10, 20)
            cv2.putText(
                self.display_image,
                coord_text,
                (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1,
                cv2.LINE_AA,
            )

        for idx, (class_id, x1, y1, x2, y2) in enumerate(self.boxes):
            color = self.get_color(class_id)
            if idx == self.selected_box_idx:
                cv2.rectangle(self.display_image, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.rectangle(self.display_image, (x1, y1), (x2, y2), color, 1)
            else:
                cv2.rectangle(self.display_image, (x1, y1), (x2, y2), color, 2)

            class_name = self.config.CLASS_NAMES.get(class_id, f"CLASS_{class_id}")
            cv2.putText(
                self.display_image,
                class_name,
                (x1, max(20, y1 - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
                cv2.LINE_AA,
            )

        if self.drawing:
            color = self.get_color(self.current_class)
            cv2.rectangle(self.display_image, self.start_point, self.end_point, color, 1)

        current_class_name = self.config.CLASS_NAMES.get(self.current_class, f"CLASS_{self.current_class}")
        selected_text = "None" if self.selected_box_idx < 0 else str(self.selected_box_idx)
        info1 = f"[{img_index + 1}/{total_images}] {image_name}"
        info2 = f"Current Class: {self.current_class} ({current_class_name}) | Selected Box: {selected_text}"

        cv2.putText(self.display_image, info1, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
        cv2.putText(self.display_image, info2, (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

        overlay = self.display_image.copy()
        cv2.rectangle(overlay, (self.image_w - 320, 10), (self.image_w - 10, 240), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.40, self.display_image, 0.60, 0, self.display_image)

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
            "q = quit",
        ]

        x_offset = self.image_w - 305
        y_offset = 30
        for line_idx, line in enumerate(shortcut_lines):
            cv2.putText(
                self.display_image,
                line,
                (x_offset, y_offset + line_idx * 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

    def mouse_callback(self, event, x, y, flags, param) -> None:
        """Handle mouse events for drawing and selecting boxes."""
        image_name, img_index, total_images = param
        self.cursor_x, self.cursor_y = x, y

        if event == cv2.EVENT_LBUTTONDOWN:
            self.selected_box_idx = -1
            self.drawing = True
            self.start_point = (x, y)
            self.end_point = (x, y)
            self.redraw(image_name, img_index, total_images)

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_point = (x, y)
            self.redraw(image_name, img_index, total_images)

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.end_point = (x, y)

            x1, y1 = self.start_point
            x2, y2 = self.end_point
            x1, y1, x2, y2 = self.clamp_box(x1, y1, x2, y2, self.image_w, self.image_h)

            min_size = int(self.config.MANUAL_MIN_BOX_SIZE)
            if abs(x2 - x1) > min_size and abs(y2 - y1) > min_size:
                self.boxes.append((self.current_class, x1, y1, x2, y2))
                self.selected_box_idx = len(self.boxes) - 1

            self.redraw(image_name, img_index, total_images)

        elif event == cv2.EVENT_RBUTTONDOWN:
            self.selected_box_idx = self.find_box_at_point(x, y)
            self.redraw(image_name, img_index, total_images)

    def run(self) -> None:
        """Start the manual annotation GUI."""
        image_files = list_image_files(self.image_dir, self.config.VALID_IMAGE_EXTS)
        if not image_files:
            print(f"No images found in: {self.image_dir}")
            return

        start_idx = int(self.config.ANNOTATION_START_FRAME_INDEX)
        if start_idx < 0 or start_idx >= len(image_files):
            print(f"Invalid ANNOTATION_START_FRAME_INDEX: {start_idx}")
            print(f"It must be between 0 and {len(image_files) - 1}.")
            return

        idx = start_idx
        window_name = str(self.config.ANNOTATION_WINDOW_NAME)
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        while 0 <= idx < len(image_files):
            image_path = image_files[idx]
            label_path = self.label_dir / f"{image_path.stem}.txt"

            self.current_image = cv2.imread(str(image_path))
            if self.current_image is None:
                print(f"Failed to load image: {image_path}")
                idx += 1
                continue

            self.image_h, self.image_w = self.current_image.shape[:2]
            self.boxes = self.load_labels(label_path)
            self.cursor_x = self.image_w // 2
            self.cursor_y = self.image_h // 2
            self.selected_box_idx = -1

            self.redraw(image_path.name, idx, len(image_files))
            cv2.setMouseCallback(
                window_name,
                self.mouse_callback,
                param=(image_path.name, idx, len(image_files)),
            )

            while True:
                cv2.imshow(window_name, self.display_image)
                key = cv2.waitKey(20) & 0xFF

                if key in [ord("1"), ord("2"), ord("3")]:
                    new_class = int(chr(key)) - 1
                    if new_class not in self.config.CLASS_NAMES:
                        print(f"Class {new_class} is not defined in CLASS_NAMES.")
                        continue

                    if self.selected_box_idx >= 0:
                        _, x1, y1, x2, y2 = self.boxes[self.selected_box_idx]
                        self.boxes[self.selected_box_idx] = (new_class, x1, y1, x2, y2)
                    else:
                        self.current_class = new_class
                    self.redraw(image_path.name, idx, len(image_files))

                elif key == ord("x"):
                    if self.selected_box_idx >= 0:
                        self.boxes.pop(self.selected_box_idx)
                        self.selected_box_idx = -1
                        self.redraw(image_path.name, idx, len(image_files))

                elif key == ord("u"):
                    if self.boxes:
                        self.boxes.pop()
                        self.selected_box_idx = -1
                        self.redraw(image_path.name, idx, len(image_files))

                elif key == ord("s"):
                    self.save_labels(label_path)
                    print(f"Saved: {label_path}")
                    self.redraw(image_path.name, idx, len(image_files))

                elif key == ord("d"):
                    self.save_labels(label_path)
                    print(f"Saved and next: {label_path}")
                    idx += 1
                    break

                elif key == ord("a"):
                    self.save_labels(label_path)
                    print(f"Saved and previous: {label_path}")
                    idx = max(0, idx - 1)
                    break

                elif key == ord("q"):
                    self.save_labels(label_path)
                    print(f"Saved and quit: {label_path}")
                    cv2.destroyAllWindows()
                    return

        cv2.destroyAllWindows()
        print("Annotation finished.")


def run_manual_annotator(config) -> None:
    """Convenience wrapper used by main.py."""
    annotator = YoloManualAnnotator(config)
    annotator.run()
