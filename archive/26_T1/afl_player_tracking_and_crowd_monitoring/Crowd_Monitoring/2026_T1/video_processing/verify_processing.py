import cv2
import os
import time
import numpy as np
from main import process_video, executor

def run_verification(video_id, video_path):
    print("=== STARTING VERIFICATION SYSTEM ===")
    
    # 1. Performance Measurement
    start_time = time.time()
    result = process_video(video_id, video_path)
    # Ensure all background threads finish before we measure time
    executor.shutdown(wait=True) 
    end_time = time.time()
    
    total_time = end_time - start_time
    num_frames = len(result.get("frames", []))
    
    print(f"\n[1] Performance Results:")
    print(f"- Total Time: {total_time:.2f} seconds")
    print(f"- Frames Processed: {num_frames}")
    if num_frames > 0:
        print(f"- Speed: {total_time/num_frames:.4f} seconds per frame")

    # 2. Visual & Structural Check
    if num_frames > 0:
        # Get the first saved frame path
        first_frame_rel_path = result["frames"][0]["frame_path"]
        # Convert relative path to absolute
        first_frame_path = os.path.join(os.getcwd(), first_frame_rel_path)
        
        # Load the image
        # Note: We use cv2.imread which loads in BGR. 
        # If your script saved it correctly as RGB, it will look 'wrong' in imread 
        # but 'right' in your AI model.
        img = cv2.imread(first_frame_path)
        
        if img is not None:
            h, w, c = img.shape
            print(f"\n[2] Image Structure Check:")
            print(f"- Resolution: {w}x{h} (Target should be 640x640)")
            
            # Check for Letterboxing (Top and Bottom bars)
            # Sample a few pixels from the very top center
            top_strip = img[0:5, w//2]
            is_letterboxed = np.mean(top_strip) < 10
            print(f"- Letterboxing Detected: {is_letterboxed}")
            
            # Check Color (Green Grass Check)
            # In a normal BGR image, Green is [0, 255, 0]. 
            # If you saved it as RGB, it's [0, 255, 0] but imread sees it as BGR.
            # We just want to ensure the image isn't grayscale or corrupted.
            has_color = not (np.allclose(img[:,:,0], img[:,:,1]) and np.allclose(img[:,:,1], img[:,:,2]))
            print(f"- Color Data Present: {has_color}")

            # Visual Display
            print("\n[3] Visual confirmation: Close the window to finish.")
            cv2.imshow("Verification - Press any key", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print(f"\n[!] Error: Could not load the saved frame at {first_frame_path}")
    else:
        print("\n[!] Error: No frames were extracted. Check your blur threshold or sample rate.")

if __name__ == "__main__":
    # Ensure paths match your project structure
    run_verification("match_01", "data/raw/match_01.mp4")