# What is small object detection?
In computer vision, a small object does not necessarily correspond to small objects in reality; rather, it indicates the object's size in relation to the entire image. This distinction is important, especially in aerial imaging, where objects may appear small because of the camera's distance.

Small object in computer vision is not imply as small objects in real life; it state the object's size relative to the overall image. This is especially important in aerial imaging, where objects might be small due to the distance of the camera.

## Why Is Detecting Small Objects Hard?
The small object is a universal problem for various object, as the COCO evaluation results for some common models YOLOv3, EfficientDet, and YOLOv4 (Akyon et al., 2022):

![performance](https://github.com/milieureka/redback-orion/blob/main/Crowd_Monitoring/small_object_detection/resources/small%20object%20perfomance.png)

From the results, focus on APs and APl column, which represent average precision scores. For instance, in EfficientDet, the AP for small objects is just 12%, compared to 51% for large objects. This shows a significant gap, nearly five-fold difference!

The difficulty YOLO models face in detecting small objects can be attributed to the model's architecture. According to Dario et al. (2021), YOLO includes multiple convolutional neural network (CNN) layers, after each CNN its result in a feature map and it get smaller till the final one. This small feature map tends to lose spatial context, which is crucial for detecting small objects. As a result, YOLO often misses these small objects in an image. More detail explanationis [here](https://learnopencv.com/slicing-aided-hyper-inference/).

![yolo](https://github.com/milieureka/redback-orion/blob/main/Crowd_Monitoring/small_object_detection/resources/yolo.jpg)

Morover, current object detection model such as Faster RCNN, YOLO, SSD, RetinaNet, EfficientDet, etc are trained on COCO (Common Objects in Context) dataset, which may contain biases toward larger objects due to their prevalence. As a consequence, the model may not have been exposed to enough diverse training examples of small objects.

## How to detect small objects (inference optimisations)
One of the approach is using is InferenceSlicer. Instead of running the model on the whole scene, InferenceSlicer splits it into smaller parts (slices), runs the model on each one, and then stitches the results together. 

Taken this idea, SAHI was introduced in a research paper "Slicing Aided Hyper Inference and Fine-Tuning for Small Object Detection" from Akyon et al. (2022). SAHI works by dividing an image into slices that completely cover it and running inference on each of these slices with a specified detection model. The predictions across all of these slices are then merged together to generate one list of detections across the entire image. The “hyper” in SAHI comes from the fact that SAHI’s output is not the result of model inference but a result of computations involving multiple model inferences. 

SAHI slices are allowed to overlap (as illustrated in the GIF below), which can help ensure that enough of an object is in at least one slice to be detected.

SAHI framework

![sahi_framework](https://github.com/milieureka/redback-orion/blob/main/Crowd_Monitoring/small_object_detection/resources/390262ac-d9c3-4987-add6-b910cbf4bc89_12.avif)

Illustration of framework, [source](https://supervision.roboflow.com/develop/how_to/detect_small_objects/#input-resolution)

![sahi_framework_illustration](https://github.com/milieureka/redback-orion/blob/main/Crowd_Monitoring/Small%20object%20detection/resources/supervision_detect_small_objects_example_2-ezgif.com-video-to-gif-converter.gif)

The key advantage of using SAHI is that it is model-agnostic. SAHI can leverage today’s SOTA object detection models and whatever the SOTA model happens to be tomorrow!

## Result on my implementation

**YOLOv5 from T1/2024**
![yolov5_t124](https://github.com/milieureka/redback-orion/blob/main/Crowd_Monitoring/small_object_detection/resources/base-yolov5.png)

**YOLOv8 + SAHI**
![yolov8_sahi](https://github.com/milieureka/redback-orion/blob/main/Crowd_Monitoring/small_object_detection/resources/yolov8%2Bsahi.png)

Only YOLOv8

![yolo_predict](https://github.com/milieureka/redback-orion/blob/main/Crowd_Monitoring/small_object_detection/resources/yolov8_predict.png)

YOLOv8 and SAHI

![yolo_predict](https://github.com/milieureka/redback-orion/blob/main/Crowd_Monitoring/small_object_detection/resources/yolov8nsahi.png)

[source_code](https://github.com/milieureka/redback-orion/blob/main/Crowd_Monitoring/small_object_detection/model.ipynb)
## Evaluation
# Reference
Here’s the corrected version of your references, formatted consistently:

1. Akyon, F., Altinuc, S. O., & Temizel, A. (2022). *Slicing aided hyper inference and fine-tuning for small object detection*. In 2022 IEEE International Conference on Image Processing (ICIP) (pp. 966-970).

2. Bochkovskiy, A., Wang, C.-Y., & Liao, H.-Y. M. (2020). *YOLOv4: Optimal speed and accuracy of object detection*. Retrieved from [https://arxiv.org/abs/2004.10934](https://arxiv.org/abs/2004.10934)

3. Oliveira, D. A. B., Pereira, L. G. R., Bresolin, T., Ferreira, R. E. P., & Dorea, J. R. R. (2021). *A review of deep learning algorithms for computer vision systems in livestock*. Livestock Science, 253, 104700.




