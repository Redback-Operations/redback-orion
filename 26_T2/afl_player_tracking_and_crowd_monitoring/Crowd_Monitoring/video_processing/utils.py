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
    cv2.imwrite(path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

def get_video_stats(full_input_path):
    """
    Analyse representative frames from the entire video to estimate
    an appropriate blur/sharpness threshold.

    The number of frames used for quality analysis is selected
    dynamically based on the video duration.

    Important:
    - The video is still decoded sequentially from start to end.
    - We only calculate the Laplacian variance on selected frames.

    Returns (dynamic_threshold, stats) - stats is a dict describing what
    was measured, for the caller to fold into one combined report instead
    of this function printing it directly.
    """

    # Open the input video.
    cap = cv2.VideoCapture(full_input_path)

    # Check that the video was opened successfully.
    if not cap.isOpened():
        # Return a safe default threshold if the video cannot be opened.
        return 100.0, {
            "note": f"Unable to open video for statistics: {full_input_path}"
        }

    # Get the total number of frames in the video.
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Get the video frame rate.
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Protect against invalid FPS values.
    if fps <= 0:
        fps = 30.0

    # Calculate the approximate video duration in seconds.
    duration = total_frames / fps

    # ---------------------------------------------------------
    # Decide how much of the video should be analysed.
    # ---------------------------------------------------------
    #
    # Short videos need a larger percentage because they contain
    # fewer frames overall.
    #
    # Longer videos can use a smaller percentage because there
    # are many more frames available to represent the video.
    #
    # These are initial engineering values and can be benchmarked
    # and adjusted later using real project videos.
    if duration <= 10:
        sampling_percentage = 0.15       # 15%

    elif duration <= 30:
        sampling_percentage = 0.10       # 10%

    elif duration <= 120:
        sampling_percentage = 0.05       # 5%

    elif duration <= 600:
        sampling_percentage = 0.02       # 2%

    else:
        sampling_percentage = 0.01       # 1%

    # Calculate how many frames should be analysed.
    statistics_samples = max(
        1,
        int(total_frames * sampling_percentage)
    )

    # ---------------------------------------------------------
    # Safety limit
    # ---------------------------------------------------------
    #
    # Very long videos could still produce a large number of
    # samples even with a small percentage.
    #
    # Therefore, we use 2,000 only as a safety limit.
    #
    # This is NOT a normal limit for our current videos.
    if statistics_samples > 2000:
        statistics_samples = 2000

    # ---------------------------------------------------------
    # Create evenly distributed frame positions.
    # ---------------------------------------------------------
    #
    # np.linspace() gives us positions distributed across the
    # entire video rather than taking only the beginning.
    #
    # For example, if we need 5 samples from a video:
    #
    # [0, 25%, 50%, 75%, 100%]
    #
    # This gives the statistics a better representation of the
    # whole video.
    sample_positions = np.linspace(
        0,
        max(total_frames - 1, 0),
        statistics_samples,
        dtype=int
    )

    # Convert the positions into a set so that checking whether
    # the current frame needs analysis is very fast.
    sample_positions = set(sample_positions)

    # Store the Laplacian variance values from sampled frames.
    variances = []

    # Keep track of the current frame number.
    count = 0

    # ---------------------------------------------------------
    # Sequentially read the video.
    # ---------------------------------------------------------
    #
    # We deliberately do NOT use:
    #
    # cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
    #
    # because random seeking in compressed video can be expensive.
    #
    # Instead, we decode the video sequentially and only perform
    # the quality calculation on selected frames.
    while True:

        # Check whether this frame was selected for statistics.
        if count in sample_positions:

            # Only fully decode (grab + retrieve) frames we actually
            # need. cap.read() would decode every frame just to
            # discard the ones outside sample_positions.
            ret, frame = cap.read()

            # Stop when there are no more frames.
            if not ret:
                break

            # Convert the selected frame to grayscale.
            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            # Calculate Laplacian variance.
            #
            # Higher variance generally indicates more edges
            # and therefore a sharper frame.
            #
            # Lower variance generally indicates blurrier content.
            variance = cv2.Laplacian(
                gray,
                cv2.CV_64F
            ).var()

            # Ignore extremely low values that are not useful
            # for calculating the threshold.
            if variance > 10:
                variances.append(variance)

        else:
            # Demux/skip this frame without decoding it. grab() is
            # far cheaper than read() since it does not decode the
            # compressed packet into a full frame.
            ret = cap.grab()

            # Stop when there are no more frames.
            if not ret:
                break

        # Move to the next frame number.
        count += 1

    # Release the video resource.
    cap.release()

    # ---------------------------------------------------------
    # Handle the case where no useful statistics were collected.
    # ---------------------------------------------------------
    base_stats = {
        "duration": round(duration, 2),
        "total_frames": total_frames,
        "sampling_percentage": sampling_percentage,
        "statistics_samples": statistics_samples,
    }

    if not variances:
        # Return the existing safe default threshold.
        return 100.0, {**base_stats, "note": "No valid variance values found."}

    # Find the minimum observed sharpness value.
    v_min = min(variances)

    # Find the maximum observed sharpness value.
    v_max = max(variances)

    # Calculate the average sharpness value.
    v_avg = sum(variances) / len(variances)

    # ---------------------------------------------------------
    # Calculate the dynamic blur threshold.
    # ---------------------------------------------------------
    #
    # We currently use 80% of the average Laplacian variance.
    #
    # This means the threshold adapts to the quality of the
    # particular video instead of always using a fixed value.
    dynamic_threshold = v_avg * 0.8

    # Return the threshold plus what it was derived from, for the caller
    # to fold into one combined report.
    return dynamic_threshold, {
        **base_stats,
        "v_min": round(v_min, 2),
        "v_max": round(v_max, 2),
        "v_avg": round(v_avg, 2),
        "threshold": round(dynamic_threshold, 2),
        "note": None,
    }

def get_detection_sample_interval(total_frames, fps):
    """
    Decide how many frames to skip between processed frames
    based on the duration of the video.

    The returned value is the frame interval 'n'.

    Example:
        n = 5
        → process frame 0, 5, 10, 15, 20, ...

    There is no total-frame limit.
    Processing continues until the end of the video.
    """

    # Protect against an invalid FPS value.
    if fps <= 0:
        fps = 30.0

    # Calculate the duration of the video in seconds.
    duration = total_frames / fps

    # Select the frame interval based on video duration.
    #
    # Shorter videos:
    #   Smaller interval → more frames processed.
    #
    # Longer videos:
    #   Larger interval → fewer frames processed.
    if duration <= 10:
        sample_interval = 3

    elif duration <= 30:
        sample_interval = 5

    elif duration <= 120:
        sample_interval = 10

    elif duration <= 600:
        sample_interval = 20

    else:
        sample_interval = 30

    # Return the selected interval.
    return sample_interval

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