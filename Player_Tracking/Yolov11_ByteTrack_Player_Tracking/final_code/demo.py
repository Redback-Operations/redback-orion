from track import Tracking
import time

def main():
    # Configuration
    start = time.time()
    model_path = 'best.pt'  #use your path
    video_path = 'afl video.mp4' #use your path
    output_path = video_path.rsplit('.', 1)[0] + "_separated_tracking_ocr.mp4" #use your path
    
    try:
        print("=== AFL Player Tracking Demo ===")
        print(f"Input video: {video_path}")
        print(f"Output video: {output_path}")
        
        # Initialize tracking module
        track_module = Tracking(
            model_path=model_path,
            confidence_threshold=0.3,
        )
        
        # Process video with output video and JSON saving
        results = track_module(
            video_path=video_path,
            output_video=output_path,
            save_json=True
        )
    except Exception as e:
        print(f"Error: {e}")

    print("Time taken: ", time.time()-start)

if __name__ == "__main__":
    main()