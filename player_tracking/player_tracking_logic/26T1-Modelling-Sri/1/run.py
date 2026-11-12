from src.video_io import open_video, create_video_writer
from src.track import PlayerTracker
from src.draw import draw_tracked_boxes
from src.csv_logger import create_csv_file, append_result_to_csv


def main():
    input_video = "videos/sample.mp4"
    output_video = "outputs/output.mp4"
    output_csv = "outputs/tracking_results.csv"
    model_path = "models/best_v1.pt"

    tracker = PlayerTracker(model_path, conf=0.3) #creates a player tracker object using the specified model and confidence threshold

    cap, fps, width, height = open_video(input_video) #opens the input video and retrieves its properties such as frames per second (fps), width, and height
    writer = create_video_writer(output_video, fps, width, height) #creates a video writer object to save the output video with the same properties as the input video

    create_csv_file(output_csv) #creates a new CSV file to store the tracking results, with appropriate headers for frame number, player ID, bounding box coordinates, and confidence score

    frame_count = 0

    while True: #loops through each frame of the video until there are no more frames to read
        ret, frame = cap.read()  #reads a frame from the video. If the frame is successfully read, ret will be True and frame will contain the image data. If there are no more frames to read, ret will be False, and the loop will break.

        if not ret:
            break

        result = tracker.track(frame) #uses the player tracker object to track players in the current frame
        frame_with_tracks = draw_tracked_boxes(frame.copy(), result) #draws bounding boxes around the tracked players in the current frame onto a copy of the original frame, using the tracking results obtained from the tracker

        writer.write(frame_with_tracks) #writes the processed frame with tracking annotations to the output video file
        append_result_to_csv(output_csv, frame_count, result) #appends the tracking results for the current frame to the CSV file

        frame_count += 1

        if frame_count % 25 == 0:
            print(f"Processed {frame_count} frames")

    cap.release() #releases the video capture object to free up system resources
    writer.release() #releases the video writer object to finalize the output video file and free up system resources

    print("Processing complete.")
    print(f"Saved video to: {output_video}")
    print(f"Saved csv to: {output_csv}")


if __name__ == "__main__":
    main()