from utils import (read_video,
                   save_video)

from trackers import PlayerTracker,BallTracker
from court_line_detector import CourtLineDetector




def main():

    #getting the input video 
    input_video_path = "input_files/input_file.mp4"
    
    #storing the video frame by frame
    video_frames = read_video(input_video_path)

    #creating an object for tracking the player
    player_tracker = PlayerTracker(model_path = 'yolov8x')
    ball_tracker = BallTracker(model_path ='models/yolov5_last.pt' )

    #contains the xyxy cordinates of the player bounding boxes
    player_detections = player_tracker.detect_frames(video_frames,
                                                     read_from_stub=False,
                                                     stub_path="tracker_stubs/player_detections.pkl")
    
    ball_detections = ball_tracker.detect_frames(video_frames,
                                                     read_from_stub=False,
                                                     stub_path="tracker_stubs/ball_detections.pkl")
    
    ball_detections = ball_tracker.interpolate_ball_positions(ball_detections)
    
    #court line detector
    court_model_path = "models/keypoints_model_dwnld.pth"
    court_line_detector = CourtLineDetector(court_model_path)
    court_keypoints = court_line_detector.predict(video_frames[0])



    #drawing the bounding boxes
    output_video_frames = player_tracker.draw_bboxes(video_frames,player_detections)
    output_video_frames = ball_tracker.draw_bboxes(output_video_frames,ball_detections)

    #drawing court keypoints
    output_video_frames = court_line_detector.draw_keypoints_on_video(output_video_frames,court_keypoints)


    save_video(output_video_frames,"output_videos/output_video.avi")

if __name__ == "__main__":
    main()