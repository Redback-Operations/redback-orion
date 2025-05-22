# Basketball-Player-Tracking-and-fatigue-Analysis
## 1. Objective
The objective of this project is to develop a real-time fatigue tracking system for basketball players using computer vision. 
By leveraging object detection and tracking algorithms, the system estimates fatigue levels of players during gameplay and overlays 
visual indicators directly on the match footage. This aims to support performance analysis and assist in injury prevention by providing 
coaches and analysts with accurate and dynamic fatigue insights.

## 2. Background and Motivation
In high-intensity sports like basketball, player fatigue plays a critical role in performance, decision-making, and injury risk. 
Traditional fatigue assessment methods are either subjective or rely on specialized wearables, which may not be accessible to all teams. 
This project bridges that gap by offering a vision-based, non-invasive fatigue analysis solution using video footage alone.

## 3. Technical Stack
- Programming Language: Python  
- Model: YOLOv8 (for player detection)  
- Tracker: Deep SORT  
- Libraries: OpenCV, NumPy, ultralytics, deep_sort_realtime  
- Platform: Google Colab / Local Jupyter Notebook  
- Input: Basketball match video (MP4)  
- Output: Annotated video with fatigue overlays

## 4. System Workflow
1. The video is read frame-by-frame.  
2. YOLOv8 detects players in each frame.  
3. Deep SORT assigns consistent IDs to players.  
4. Player positions are recorded across frames.  
5. Speed, variability, and duration are calculated.  
6. Fatigue score is computed.  
7. Visual overlays (fatigue level, bars, alerts) are added.  
8. The final annotated video is saved.

## 5. Fatigue Score Calculation
Fatigue is computed using three key motion-based metrics:
- Speed Drop (%) = (initial_avg_speed - final_avg_speed) / initial_avg_speed * 100  
- Speed Variability = Standard deviation of last 25 speed values  
- Duration = Number of frames tracked / FPS  

These are normalized and combined:
```
fatigue_score = 0.4 * drop_score + 0.3 * var_score + 0.3 * dur_score
```

## 6. Features Implemented
- Real-time player detection and identity tracking  
- Speed estimation in meters per second  
- Fatigue level estimation using motion trends  
- Fatigue bar visual indicator  
- Top 3 fatigue dashboard display  
- FATIGUE SPIKE alerts  
- Transparent overlay with frame, player count, avg fatigue

## 7. Code Logic Overview
Each tracked player’s position is stored to compute speed.  
If enough frames are tracked, fatigue is estimated and overlays are drawn:
- Bounding boxes change color based on fatigue level  
- Text displays ID, speed, fatigue level  
- Horizontal bar fills based on fatigue score  
- Top 3 fatigued players shown on a live dashboard  
- A bottom overlay provides frame stats

## 8. Dataset Preparation and Annotation
The dataset used for training the YOLOv8 model was curated from basketball video footage and annotated using Roboflow. 
This platform provided a streamlined environment for creating bounding boxes around players and exporting annotations in YOLO format. 
Annotated images were then used to fine-tune the detection model for optimal performance in sports environments.
## Dataset Access (from Roboflow)

This project uses a custom basketball player dataset annotated using Roboflow.

To download the YOLOv8-compatible dataset:

```python
!pip install roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="LqKpTXknZOXpFqSOBqjF")
project = rf.workspace().project("player-tracking-dv9lo")
dataset = project.version(1).download("yolov8")
```

## 9. Challenges Faced
- Maintaining tracking accuracy under occlusions  
- Estimating fatigue from limited frame-based data  
- Avoiding overlay clutter in visualizations  
- Balancing precision and real-time performance

## 10. Evaluation and Output Analysis
The final system was tested on real basketball gameplay footage with resolution 1920x1080 at 30 FPS. 
The tracker maintained stable player identities and displayed fatigue metrics in real-time with minimal frame drops. 
Fatigue classifications appeared realistic based on player movements, and visual overlays (fatigue bars, labels, dashboard) remained unobtrusive yet informative.

## 11. Future Enhancements
- Integrate total distance and direction change metrics  
- Export player-level fatigue statistics to CSV dashboards  
- Deploy for real-time use in live match settings  
- Extend system to multi-sport scenarios like soccer or hockey

## 12. Conclusion
This project demonstrates a successful application of computer vision to real-time player fatigue analysis. 
By combining YOLOv8 detection with Deep SORT tracking and realistic fatigue modeling, the system delivers a non-invasive solution for coaches and analysts. 
Visual indicators, dynamic scoring, and intuitive overlays make the tool practical, scalable, and effective for sports performance analysis.

## 13. References
- Bochkovskiy, A., Wang, C.-Y., & Liao, H.-Y. M. (2020). YOLOv4: Optimal Speed and Accuracy of Object Detection. arXiv:2004.10934  
- Wojke, N., Bewley, A., & Paulus, D. (2017). Simple Online and Realtime Tracking with a Deep Association Metric. IEEE ICIP  
- Ultralytics YOLOv8 Documentation: https://docs.ultralytics.com  
- Deep SORT GitHub: https://github.com/mikel-brostrom/Yolov5_DeepSort_Pytorch  
- OpenCV Docs: https://docs.opencv.org  
- Roboflow: https://roboflow.com (used for dataset annotation)
