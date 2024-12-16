from utils_sahi import*


# Function to get pixel-to-cm ratio based on the size of the football in the frame
def calculate_pixel_to_m_ratio(football_bbox, actual_diameter_m=0.21):
    diameter_pixels = calculate_distance((football_bbox.minx, football_bbox.miny), (football_bbox.maxx, football_bbox.maxy))
    pixel_to_m_ratio = actual_diameter_m / diameter_pixels
    return pixel_to_m_ratio


def calculate_distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

# Function to calculate the velocity of the football
def calculate_speed(last_pos, current_pos, fps,inc_frame, pixel_to_m_ratio):
    distance_pixels = calculate_distance(last_pos, current_pos)
    distance_m = distance_pixels * pixel_to_m_ratio 
    speed_m_per_s = distance_m * fps  
    speed_m_per_s=speed_m_per_s/inc_frame
    return speed_m_per_s


def get_video_prediction_with_speed(video_path, detection_model, yolo_model, slice_height=256, slice_width=256, 
                                       overlap_height_ratio=0.2, overlap_width_ratio=0.2, output_video_path=None, dis_thres=100):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Error opening video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if output_video_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    yolocnt = 0
    sahicnt = 0
    zerocnt = 0
    last_pos = None
    prev_pos = None  
    last_frame=0
    speed = 0  

    while True:
        ret, frame = cap.read()
        if not ret:
            break  
        print(f"frame {yolocnt + sahicnt + zerocnt}")
        current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)

        result_yolo = yolo_model.predict(frame)
        result_yolo = result_yolo[0]

        # If YOLO detects nothing
        if result_yolo.boxes.shape[0] == 0: 
            # Fall back to SAHI detection
            result_sahi = get_sliced_prediction(
                frame,
                detection_model,
                slice_height=slice_height,
                slice_width=slice_width,
                overlap_height_ratio=overlap_height_ratio,
                overlap_width_ratio=overlap_width_ratio,
            )
            
            object_prediction_list = result_sahi.object_prediction_list

            if len(object_prediction_list) == 0:
                cv2.putText(frame, f'SAHI: detected 0 items.', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                zerocnt += 1
            else:
                cv2.putText(frame, f'SAHI: detected {len(object_prediction_list)} items.', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                for object_prediction in object_prediction_list:
                    frame = draw_bbox_sahi(frame, object_prediction)
                sahicnt += 1
                last_pos = get_center(object_prediction_list[0].bbox)
                
                if last_pos and prev_pos:
                    pixel_to_m_ratio=calculate_pixel_to_m_ratio(object_prediction_list[0].bbox)
                    inc_frame=current_frame-last_frame
                    speed = calculate_speed(prev_pos, last_pos, fps,inc_frame, pixel_to_m_ratio)
  
                    #cv2.putText(frame, f'Speed: {speed:.2f} px/s', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    cv2.putText(frame, f'Football Speed: {speed:.2f} m/s', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
               
                prev_pos = last_pos  
                last_frame=current_frame

        else:
            yolocnt += 1
            tmp_boxes = []
            for box in result_yolo.boxes:
                if dis(last_pos, get_center(trans_to_bbox(box))) < dis_thres:
                    tmp_boxes.append(box)
            for box in result_yolo.boxes:
                frame = draw_bbox_yolo(frame, box, "football")
            
            if len(tmp_boxes) > 0:
                last_pos = get_center(trans_to_bbox(tmp_boxes[0]))

            if len(tmp_boxes) and last_pos and prev_pos:
                pixel_to_m_ratio=calculate_pixel_to_m_ratio(trans_to_bbox(tmp_boxes[0]))
                inc_frame=current_frame-last_frame
                speed = calculate_speed(prev_pos, last_pos, fps,inc_frame, pixel_to_m_ratio)
  
                #cv2.putText(frame, f'Speed: {speed:.2f} px/s', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(frame, f'Football Speed: {speed:.2f} m/s', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            prev_pos = last_pos  
            last_frame=current_frame

        if output_video_path:
            out.write(frame)
        cv2.imwrite(os.path.join("out_img", f'{sahicnt + yolocnt + zerocnt}.jpg'), frame)

    print("over")
    print(f"yolocnt: {yolocnt}")
    print(f"sahicnt: {sahicnt}")
    print(f"zerocnt: {zerocnt}")
    
    cap.release()
    if output_video_path:
        out.release()