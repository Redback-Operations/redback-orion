import cv2
import os
import json

#Logic to find the config relative to the Project Root
#By doing this, the code works on any computer because it doesn't care about the folders above the project(our project is at 2026_T1 folder level)
BASE_DIR = os.getcwd()
#join() is used to build a path to json config file 
CONFIG_PATH = os.path.join(BASE_DIR, "shared", "config", "video_processing_config.json")

#Important paths and parameters are stored in this config file which can be updated if needed
#We load and read that config file
def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def process_video(video_path: str):
    """
    video_path: Expected as 'data/raw/filename.mp4' (relative to Root (2026_T1))
    """
    config = load_config()
    
    #normpath will clean up any accidental double slashes (like data//raw) to ensure the OS can find the file
    #contains path where input video is present
    full_input_path = os.path.normpath(os.path.join(BASE_DIR, video_path))
    
    #contains path where output frames will be stored
    output_dir = os.path.join(BASE_DIR, config["extracted_frames_dir"])
    #it creates folder where output frames will be stored if only folder is already not created
    os.makedirs(output_dir, exist_ok=True)
    
    #opens video stream
    cap = cv2.VideoCapture(full_input_path)
    #if video file is corrupted or path is wrong we return an error
    if not cap.isOpened():
        return {"error": f"Could not open video at {full_input_path}"}

    #We store frames per second of video, if opencv cant find out we fallback to 30fps to avoid division by zero error later
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    #store config resolution size which we want frames to be in
    res_w, res_h = config["output_resolution"]
    
    frames_metadata = []
    count = 0
    extracted_count = 1 

    print(f"--- Processing Video: {video_path} ---")

    try:
        while True:
            #we read video frame by frame
            ret, frame = cap.read()
            #if no frames left, we get out of loop
            if not ret: break
            
            #Frame Sampling (We take snapshot every 30 frames, instead of taking snapshot of all frames) 
            if count % config["sample_rate"] == 0:
                #Resize for the Detection model
                resized = cv2.resize(frame, (res_w, res_h))
                
                #frame naming for maintaining frame order
                fname = f"frame_{extracted_count:04d}.jpg"
                save_path = os.path.join(output_dir, fname)
                #saving frame to output directory
                cv2.imwrite(save_path, resized)
                
                #Match the 'DetectionFrame' schema in shared/models.py
                frames_metadata.append({
                    "frame_id": extracted_count,
                    #this will tell us at what time the frame is present in video
                    "timestamp": round(count / fps, 2),
                    "frame_path": f"{config['extracted_frames_dir']}/{fname}"
                })
                extracted_count += 1
            count += 1
    finally:
        #This "closes" the video file. If we don't do this, the computer might keep the file "locked," and we won't be able to delete or move it until we restart the PC
        cap.release()

    #Return the dictionary for the Service Layer to use
    return {
        "video_path": video_path,
        "frames": frames_metadata
    }

if __name__ == "__main__":
    #Run this from the Project Root (2026_T1)
    #python -m video_processing.main
    test_res = process_video("data/raw/match_01.mp4")
    print(f"Successfully processed {len(test_res['frames'])} frames.")


#Things to improve
#1. Multi threaded frame processing, to save images in the background while the main loop keeps reading the video
#2. Batch Processing multiple videos
#3. Dynamic Sampling rate change if the Person Count is very high to get more details and decrease it when area is empty to save space

#Edge Cases to look for in future
#1. Aspect Ratio Distortion: When you resize to 640x640, a wide AFL field might look "squashed. "Fix: Use Letterboxing (adding black bars) to keep the original shape while still hitting the 640x640 target.
#2. Motion Blur. The Fix: Ensure you are extracting Keyframes (I-frames) where possible, as these contain the most complete visual data.
#3. Overcompression The Fix: Always save frames with high JPEG quality (90-95). Code: cv2.imwrite(path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
#4. Poor Normalization (Lighting/Contrast) The Fix: In the future, you can add Histogram Equalization to your processing flow to balance the lighting before the AI sees it.
#5. For person far away. The Fix: If the team needs to detect people in the far distance, you might need to implement Tiling (chopping the 4K frame into four 640x640 blocks) instead of shrinking the whole thing.