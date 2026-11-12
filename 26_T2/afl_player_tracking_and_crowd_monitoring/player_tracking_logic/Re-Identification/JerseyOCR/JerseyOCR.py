import cv2
import numpy as np
import easyocr
from collections import defaultdict, Counter 

class JerseyOCR:
    
    """
    Jersey OCR system to extract player jersey numbers from image crops.
        - Extracts jersey region from player bounding box
        - Applies preprocessing for OCR robustness
        - Runs OCR inference using EasyOCR
        - Maintains temporal voting per track for stable number prediction

    Input:
        - crops (List[np.array]): list of player image crops (BGR format)

    Output:
        - jersey_numbers (List[int or None]):
            Detected jersey numbers for each crop
            None if OCR fails
    """

    def __init__(self, use_gpu=True):
        """
        Initialize OCR engine.

        Parameters:
            - use_gpu (bool): whether to use GPU for OCR inference
        """
        self.reader = easyocr.Reader(['en'], gpu=use_gpu)

        # Track-wise voting buffer
        self.ocr_memory = defaultdict(list)

    def extract_jersey_patch(self, crop):
        """
        Extract jersey region (torso area) from player crop.

        Input:
            - crop (np.array): full player bounding box image

        Output:
            - patch (np.array): cropped jersey region
        """
        if crop is None or crop.size == 0:
            return None

        h, w, _ = crop.shape

        # Focus on torso (empirically best for AFL)
        return crop[int(0.2*h):int(0.6*h), int(0.2*w):int(0.8*w)]

    def preprocess(self, patch):
        """
        Preprocess image for OCR robustness.

        Steps:
            - Convert to grayscale
            - Gaussian blur (reduce noise)
            - Adaptive threshold (handle lighting)

        Input:
            - patch (np.array)

        Output:
            - processed image (np.array)
        """
        gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        thresh = cv2.adaptiveThreshold(
            blur,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

        return thresh.astype(np.uint8)

    def run_ocr(self, images):
        """
        Run OCR on a batch of images.

        Input:
            - images (List[np.array]): list of preprocessed images

        Output:
            - results (List[List]): OCR outputs per image
        """
        results = []
        for image in images:
            if image is None or image.size == 0:
                results.append([])
                continue

            # Ensure image is uint8
            if image.dtype != np.uint8:
                image = (image * 255).astype(np.uint8)

            result = self.reader.readtext(image, detail=1, paragraph=False)
            results.append(result)

        return results

    def extract_number(self, ocr_result):
        """
        Extract valid jersey number from OCR output.

        Input:
            - ocr_result: OCR output for a single image

        Output:
            - jersey_number (int or None)
        """
        for (_, text, conf) in ocr_result:
            if text.isdigit() and conf > 0.5:
                return int(text)

        return None

    def process_batch(self, crops, track_ids=None):
        """
        Full OCR pipeline for batch processing.
            - Extract jersey patches
            - Preprocess
            - Run OCR (GPU)
            - Extract numbers
            - Apply temporal voting

        Input:
            - crops (List[np.array]): player crops
            - track_ids (List[int], optional): associated track IDs

        Output:
            - final_numbers (List[int or None]):
                stable jersey numbers after voting
        """

        patches = []
        valid_indices = []

        # Step 1: Extract patches
        for i, crop in enumerate(crops):
            patch = self.extract_jersey_patch(crop)

            if patch is None or patch.size == 0:
                continue
            #Block if patchs too small
            if patch.shape[0] < 12 or patch.shape[1] < 12:
                continue

            processed = self.preprocess(patch)

            patches.append(processed)
            valid_indices.append(i)

        if len(patches) == 0:
            return [None] * len(crops)

        # Step 2: OCR inference (GPU)
        ocr_outputs = self.run_ocr(patches)

        # Step 3: Extract numbers
        raw_numbers = [None] * len(crops)

        for idx, ocr_out in zip(valid_indices, ocr_outputs):
            raw_numbers[idx] = self.extract_number(ocr_out)

        # Step 4: Temporal voting
        final_numbers = [None] * len(crops)

        if track_ids is not None:
            for i, (track_id, number) in enumerate(zip(track_ids, raw_numbers)):

                if track_id is None:
                    continue

                if number is not None:
                    self.ocr_memory[track_id].append(number)

                # Keep buffer size fixed
                if len(self.ocr_memory[track_id]) > 10:
                    self.ocr_memory[track_id].pop(0)

                # Majority vote
                if len(self.ocr_memory[track_id]) >= 3:
                    final_numbers[i] = Counter(self.ocr_memory[track_id]).most_common(1)[0][0]

        else:
            final_numbers = raw_numbers

        return final_numbers