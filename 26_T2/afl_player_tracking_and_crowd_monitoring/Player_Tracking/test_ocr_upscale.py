#!/usr/bin/env python3
"""OCR test with upscaling - compare against the plain version.

Usage:
    python test_ocr_upscale.py outputs/jersey_crops/track_1367/frame_900.jpg
"""

import sys
from pathlib import Path

import cv2
import easyocr

def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python test_ocr_upscale.py <image>")

    img_path = Path(sys.argv[1])
    reader = easyocr.Reader(['en'], gpu=False)

    img = cv2.imread(str(img_path))
    h, w = img.shape[:2]
    print(f"Original size: {w}x{h}")

    # Try without allowlist first, to see if the detector finds ANY text
    print("\n--- No allowlist, original size ---")
    results = reader.readtext(img)
    for bbox, text, conf in results:
        print(f"  '{text}' (conf={conf:.2f})")
    if not results:
        print("  (nothing detected)")

    # Upscale 3x and retry
    upscaled = cv2.resize(img, (w * 3, h * 3), interpolation=cv2.INTER_CUBIC)
    cv2.imwrite("debug_upscaled.jpg", upscaled)
    print(f"\n--- No allowlist, upscaled to {w*3}x{h*3} (saved as debug_upscaled.jpg) ---")
    results = reader.readtext(upscaled)
    for bbox, text, conf in results:
        print(f"  '{text}' (conf={conf:.2f})")
    if not results:
        print("  (nothing detected)")

    # Upscale + digit-only allowlist
    print(f"\n--- Digits-only allowlist, upscaled ---")
    results = reader.readtext(upscaled, allowlist='0123456789')
    for bbox, text, conf in results:
        print(f"  '{text}' (conf={conf:.2f})")
    if not results:
        print("  (nothing detected)")

if __name__ == "__main__":
    main()
