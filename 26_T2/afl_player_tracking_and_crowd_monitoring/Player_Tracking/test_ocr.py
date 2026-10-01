#!/usr/bin/env python3
"""Quick OCR test against jersey crops.

Usage:
    python test_ocr.py outputs/jersey_crops/track_1367/frame_900.jpg
    python test_ocr.py outputs/jersey_crops/track_1367/          # whole folder
"""

import sys
from pathlib import Path
from collections import Counter

import easyocr

def read_number(reader, image_path):
    """Run OCR on one crop, return (best_guess_text, confidence) or (None, 0)."""
    results = reader.readtext(str(image_path), allowlist='0123456789')
    if not results:
        return None, 0.0
    # Pick the highest-confidence result
    best = max(results, key=lambda r: r[2])
    text, conf = best[1], best[2]
    return text, conf

def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python test_ocr.py <image_or_folder>")

    target = Path(sys.argv[1])
    reader = easyocr.Reader(['en'], gpu=False)

    if target.is_dir():
        images = sorted(target.glob("*.jpg"))
        print(f"Running OCR on {len(images)} crops in {target}\n")
        votes = Counter()
        for img in images:
            text, conf = read_number(reader, img)
            status = f"{text} (conf={conf:.2f})" if text else "no text detected"
            print(f"  {img.name}: {status}")
            if text:
                votes[text] += 1
        print("\n--- Majority vote result ---")
        if votes:
            winner, count = votes.most_common(1)[0]
            print(f"Most common reading: '{winner}' ({count}/{len(images)} frames)")
            print(f"All votes: {dict(votes)}")
        else:
            print("No readable text in any frame.")
    else:
        text, conf = read_number(reader, target)
        if text:
            print(f"Detected: '{text}' (confidence: {conf:.3f})")
        else:
            print("No text detected.")

if __name__ == "__main__":
    main()
