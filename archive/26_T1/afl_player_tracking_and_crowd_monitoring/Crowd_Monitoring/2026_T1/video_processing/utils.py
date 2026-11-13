import cv2
import numpy as np

def save_frame_worker(path, image):
    """
    Background worker to save images. 
    Note: We save with high JPEG quality (95) to preserve crowd details.
    """
    # If your main loop uses BGR (OpenCV default), no need to convert.
    # If your main loop converts to RGB for AI models, uncomment the line below:
    # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    enhanced = apply_clahe_enhancement(image)
    cv2.imwrite(path, enhanced, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

def get_video_stats(full_input_path, sample_rate):
    """
    Scans the video to find the range of sharpness (min/max Laplacian variance).
    Returns a calculated baseline threshold.
    """
    cap = cv2.VideoCapture(full_input_path)
    variances = []
    
    # Sample every decided frame_rate to get a fast but accurate representation
    count = 0
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        if count % sample_rate == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if var > 10: # Ignore pitch black/empty frames
                variances.append(var)
        count += 1
    
    cap.release()

    if not variances:
        return 100.0 # Fallback
    
    v_min = min(variances)
    v_max = max(variances)
    v_avg = sum(variances) / len(variances)
    
    # DECISION LOGIC: 
    # We want a threshold that is higher than the minimum, 
    # but not so high that we reject everything.
    # A good 'dynamic' threshold is 80% of the average.
    dynamic_threshold = v_avg * 0.8
    
    print(f"Stats - Min: {v_min:.2f}, Max: {v_max:.2f}, Avg: {v_avg:.2f}")
    print(f"Calculated Threshold: {dynamic_threshold:.2f}")
    
    return dynamic_threshold

def check_blur(image, threshold):
    """
    Computes the Laplacian variance to measure focus.
    Higher value = Sharper image. Lower value = Blurrier image.
    100.0 is a good starting point for 1080p footage
    """
    #Converting from BGR to Grayscale because computers dont need full color image to detect sharpness, they only need intensity (brightness changes), and processing one channel(gray) is faster than 3 channels
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #kernel (a small matrix) applied over image to find edges (a place where a light pixel is right next to dark pixel)
    #var() variance between these contrasting pixel values.
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance, variance >= threshold

import cv2

def apply_clahe_enhancement(image):
    # Convert BGR to LAB color space to get access of Lightness channel
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    # Split the LAB image into separate channels
    l_channel, a_channel, b_channel = cv2.split(lab)
    
    # Create the CLAHE object
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    
    # Apply CLAHE to the L (Lightness) channel
    # clahe.apply() function redistributes the pixel intensities in the L-channel so that the "histogram" (the distribution of darks and lights) is flatter and wider, making details in shadows visible
    l_enhanced = clahe.apply(l_channel)
    
    # Merge the enhanced L channel back with original A and B channels
    enhanced_lab = cv2.merge((l_enhanced, a_channel, b_channel))
    
    # Convert back to BGR color space
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)