#!/usr/bin/env python3

def prepare_tracking() -> None:
    import cv2
    import imageio_ffmpeg
    from ultralytics import YOLO


prepare_tracking()

from review_tool.app import main


if __name__ == "__main__":
    main()
