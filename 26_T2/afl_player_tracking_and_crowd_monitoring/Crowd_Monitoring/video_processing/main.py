import cv2
import os
import json  
import time                 # Used for pipeline performance timing
from concurrent.futures import ThreadPoolExecutor # For background file saving
# Import utils
from video_processing.utils import get_video_stats, check_blur, save_frame_worker, apply_clahe_enhancement, get_detection_sample_interval
from video_processing.tiling import generate_tiles

#Logic to find the config relative to the Project Root
#By doing this, the code works on any computer because it doesn't care about the folders above the project(our project is at 2026_T1 folder level)
BASE_DIR = os.getcwd()
#join() is used to build a path to json config file 
CONFIG_PATH = os.path.join(BASE_DIR, "shared", "config", "video_processing_config.json")

#max_workers 4 reserved for writing extracted frame to folder where we want to save 
executor = ThreadPoolExecutor(max_workers=4)

#Important paths and parameters are stored in this config file which can be updated if needed
#We load and read that config file
def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def runtime_preprocessing(frame, config):
    """
    Runtime preprocessing stage for the T2 pipeline.

    Current implementation:
        - Configurable tiling.
        - Configurable tile overlap.
        - Conditional CLAHE.

    Future additions:
        - Use video-level quality thresholds
          calculated during video analysis.
        
    The frame is currently returned unchanged unless
    tiling is enabled.
    """

    # --------------------------------------------------------
    # FUTURE: QUALITY-BASED PREPROCESSING
    # --------------------------------------------------------
    #
    # Video-level quality statistics will be calculated
    # during the initial video analysis stage.
    #
    # For example:
    #
    #     blur threshold
    #     contrast threshold
    #     brightness threshold
    #     sharpness threshold
    #
    # The current frame can later be compared against
    # these thresholds here to determine whether
    # preprocessing such as CLAHE is required.
    #
    # --------------------------------------------------------


    # For now, keep the original frame unchanged.
    processed_frame = frame


    # --------------------------------------------------------
    # CURRENT: CONFIGURABLE TILING
    # --------------------------------------------------------

    tiling_enabled = config.get(
        "enable_tiling",
        False
    )


    tiles = []
    tile_metadata = []


    if tiling_enabled:

        tile_rows = config.get(
            "tile_rows",
            2
        )

        tile_columns = config.get(
            "tile_columns",
            2
        )

        # ----------------------------------------------------
        # CURRENT T2: CONFIGURABLE TILE OVERLAP
        # ----------------------------------------------------
        #
        # The overlap value is read from the configuration.
        #
        # Example:
        #
        # tile_overlap = 0.10
        #
        # means neighbouring tiles overlap by approximately
        # 10% of their tile dimensions.
        #
        # generate_tiles() dynamically calculates the tile
        # dimensions and positions so that the complete
        # frame is covered without gaps.
        # ----------------------------------------------------
        tile_overlap = config.get(
            "tile_overlap",
            0.0
        )

        tiles, tile_metadata = generate_tiles(
            processed_frame,
            rows=tile_rows,
            cols=tile_columns,
            overlap=tile_overlap
        )


    return (
        processed_frame,
        tiles,
        tile_metadata
    )

def process_video(video_id: str, video_path: str):
    """
    video_path: Expected as 'data/raw/filename.mp4' (relative to Root (2026_T1))
    """
    #measures the actual wall-clock duration of the complete Video Processing operation(Benchmark)
    pipeline_start = time.perf_counter()

    config = load_config()
    
    #normpath will clean up any accidental double slashes (like data//raw) to ensure the OS can find the file
    #contains path where input video is present
    full_input_path = os.path.normpath(os.path.join(BASE_DIR, video_path))
    
    # Existing video quality analysis.
    #
    # CURRENT:
    #   Calculates the dynamic blur threshold.
    #
    # FUTURE:
    #   Extend this analysis stage to also calculate
    #   video-level contrast, brightness and sharpness
    #   statistics and derive their thresholds.
    #
    # This keeps all video-level quality analysis
    # in one place rather than creating a separate
    # quality-analysis pass.

    #(Benchmark)
    stats_start = time.perf_counter()

    # If variance is less then threshold blurry image else sharp image
    dynamic_threshold, video_stats = get_video_stats(full_input_path)

    #(Benchmark)
    stats_time = time.perf_counter() - stats_start


    # ------------------------------------------------------------
    # Frame Paths
    # ------------------------------------------------------------
    #contains path where output frames will be stored
    output_dir = os.path.join(BASE_DIR, config["extracted_frames_dir"])
    #It creates folder where output frames will be stored if only folder is already not created
    os.makedirs(output_dir, exist_ok=True)

    
    #opens video stream
    cap = cv2.VideoCapture(full_input_path)
    #if video file is corrupted or path is wrong we return an error
    if not cap.isOpened():
        return {"error": f"Could not open video at {full_input_path}"}

    #We store frames per second of video, if opencv cant find out we fallback to 30fps to avoid division by zero error later
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

    # Get the total number of frames in the video.
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate the frame interval based on the video duration.
    # For example, if this returns 5, we process every 5th frame.
    detection_sample_interval = get_detection_sample_interval(
        total_frames,
        fps
    )
    
    frames_metadata = []
    save_futures = []
    count = 0
    extracted_count = 1 

    #Counters for benchmark(Benchmark)
    total_blur_time = 0.0
    total_tiling_time = 0.0
    total_frames_read = 0
    total_tiles_generated = 0

    total_clahe_time = 0.0
    total_clahe_frames = 0
    total_decoding_time = 0.0
    total_main_read_time = 0.0
    total_recovery_read_time = 0.0
    total_jpeg_time = 0.0
    total_sampled_frames = 0
    total_processed_frames = 0

    try:
        while True:
            # Only a frame landing on the sampling interval is actually used
            # below; the rest were previously fully decoded via cap.read()
            # and immediately discarded. grab() skips the costly
            # retrieve()/colour-convert step for those - same fix applied to
            # get_video_stats() above.
            next_count = count + 1
            needed = (next_count % detection_sample_interval == 0)

            #(Benchmark)
            decode_start = time.perf_counter()
            if needed:
                #we read video frame by frame
                ret, frame = cap.read()
            else:
                ret = cap.grab()
                frame = None
            #(Benchmark)
            decode_time = time.perf_counter() - decode_start
            total_decoding_time += decode_time
            total_main_read_time += decode_time

            #if no frames left, we get out of loop
            if not ret: break

            # Increase the frame counter immediately after successfully reading a frame.
            count = next_count

            #Tells how much video was processed(Benchmark)
            total_frames_read += 1

            #Dynamic Frame Sampling (We take snapshot every nth frames, instead of taking snapshot of all frames based on video duration)
            if needed:
                #Total sampled frames(Benchmark)
                total_sampled_frames += 1
                #Measure blur detection time(Benchmark)
                blur_start = time.perf_counter()
                score, is_sharp = check_blur(frame, dynamic_threshold)
                #Measure blur detection time(Benchmark)
                total_blur_time += time.perf_counter() - blur_start
                
                # If the camera is panning or shaking(blurry frame), check the next few frames.
                # Crowd faces are unrecognizable in motion blur.
                search_count = 0
                while not is_sharp and search_count < 8: # Slightly longer window for crowd stabilization
                    #(Benchmark)
                    recovery_start = time.perf_counter()
                    ret, frame = cap.read()
                    #(Benchmark)
                    recovery_time = time.perf_counter() - recovery_start
                    total_decoding_time += recovery_time
                    total_recovery_read_time += recovery_time

                    if not ret: break

                    # Recovery has consumed another actual video frame, so update the frame counter.
                    count += 1
                    # Count how many recovery attempts have been made.
                    search_count += 1
                    #Measure blur detection time(Benchmark)
                    blur_start = time.perf_counter()
                    score, is_sharp = check_blur(frame, dynamic_threshold)
                    #Measure blur detection time(Benchmark)
                    total_blur_time += time.perf_counter() - blur_start


                # ------------------------------------------------------------
                # CONDITIONAL CLAHE ENHANCEMENT
                # ------------------------------------------------------------
                if not is_sharp:
                    total_clahe_frames += 1
                    clahe_start = time.perf_counter()

                    processed_frame = apply_clahe_enhancement(frame)

                    total_clahe_time += time.perf_counter() - clahe_start
                else:
                    # Frame quality is already acceptable, so skip CLAHE.
                    processed_frame = frame



                # ------------------------------------------------------------
                # T2 RUNTIME PREPROCESSING
                # ------------------------------------------------------------
                #
                # Current:
                #   - Configurable tiling.
                #   - Configurable tile overlap.
                #   - Conditional CLAHE.
                #
                # Future:
                #   - Compare current-frame quality against
                #     video-level thresholds.
                #
                #Measure tiling time(Benchmark)
                tiling_start = time.perf_counter()
                processed_frame, tiles, tile_metadata = runtime_preprocessing(
                    processed_frame,
                    config
                )
                #Measure tiling time(Benchmark)
                tiling_time = time.perf_counter() - tiling_start
                total_tiling_time += tiling_time
                total_tiles_generated += len(tiles)

                

                #frame naming for maintaining frame order
                fname = f"frame_{extracted_count:04d}.jpg"
                save_path = os.path.join(output_dir, fname)
                
                save_futures.append(executor.submit(save_frame_worker, save_path, processed_frame))


                #Match the 'DetectionFrame' schema in shared/models.py
                frames_metadata.append({
                    "frame_id": extracted_count,
                    #this will tell us at what time the frame is present in video
                    "timestamp": round(count / fps, 2),
                    "frame_path": f"{config['extracted_frames_dir']}/{fname}",
                    # Attach tile metadata to this frame.
                    # If tiling is disabled, this will simply be an empty list.
                    "tiles": tile_metadata
                })
                    
                #(Benchmark)
                total_processed_frames += 1
                extracted_count += 1
    finally:
        #This "closes" the video file. If we don't do this, the computer might keep the file "locked," and we won't be able to delete or move it until we restart the PC
        cap.release()

    #(Benchmark)
    jpeg_start = time.perf_counter()
    for future in save_futures:
        future.result()
    #(Benchmark)
    jpeg_time = time.perf_counter() - jpeg_start

    #Measure end to end time(Benchmark)
    pipeline_time = time.perf_counter() - pipeline_start

    # Benchmark numbers are returned rather than printed here, so the
    # caller can fold them into one combined report instead of this
    # function printing its own block mid-run.
    timings = {
        "video_stats": video_stats,
        "dynamic_threshold": round(dynamic_threshold, 2),
        "stats_seconds": round(stats_time, 4),
        "decoding_seconds": round(total_decoding_time, 4),
        "main_read_seconds": round(total_main_read_time, 4),
        "recovery_read_seconds": round(total_recovery_read_time, 4),
        "blur_seconds": round(total_blur_time, 4),
        "clahe_seconds": round(total_clahe_time, 4),
        "tiling_seconds": round(total_tiling_time, 4),
        "jpeg_write_seconds": round(jpeg_time, 4),
        "total_seconds": round(pipeline_time, 4),
        "frames_read": total_frames_read,
        "sampled_frames": total_sampled_frames,
        "processed_frames": total_processed_frames,
        "clahe_frames": total_clahe_frames,
        "tiles_generated": total_tiles_generated,
    }

    #Return the dictionary for the Service Layer to use
    return {
        "video_id": video_id,
        "video_path": video_path,
        "frame_width": frame_width,
        "frame_height": frame_height,
        "frames": frames_metadata,
        "timings": timings,
    }

if __name__ == "__main__":
    # Run the integrated video-processing pipeline.
    #
    # Tiling configuration is now read from:
    #
    # shared/config/video_processing_config.json
    #
    # Example:
    #
    # "enable_tiling": true
    # "tile_rows": 3
    # "tile_columns": 3
    # "tile_overlap": 0.10
    #
    # Therefore, the test below verifies that the complete
    # pipeline correctly reads the configuration and passes
    # the tiling settings to generate_tiles().

    test_res = process_video(
        "side",
        "data/raw/side.mp4"
    )

    if "error" in test_res:
        print(test_res["error"])

    else:
        print(
            f"Successfully processed "
            f"{len(test_res['frames'])} frames."
        )
        print(test_res["timings"])