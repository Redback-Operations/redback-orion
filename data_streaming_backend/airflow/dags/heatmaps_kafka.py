import os
import tempfile
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator

# DAG default arguments
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Use safe, system temporary directory
tmp_dir = tempfile.gettempdir()

# Environment Variables
ENV_VARS = {
    'KAFKA_BOOTSTRAP_SERVER': os.getenv('KAFKA_BOOTSTRAP_SERVER', 'redback.it.deakin.edu.au:9092'),
    'IMAGE_TOPIC': 'heatmap',
    'RESULTS_TOPIC': 'heatmap_results',
    'YOLO_WEIGHTS': os.path.join(tmp_dir, 'yolov4.weights'),
    'YOLO_CONFIG': os.path.join(tmp_dir, 'yolov4.cfg'),
    'COCO_NAMES': os.path.join(tmp_dir, 'coco.names'),
    'TMP_OUTPUT_DIR': tmp_dir  # Optional for saving plots
}

def process_image_blob_and_generate_heatmap():
    import os
    import io
    import json
    import urllib.request
    import numpy as np
    import matplotlib.pyplot as plt
    from PIL import Image
    from kafka import KafkaConsumer, KafkaProducer
    from mpl_toolkits.mplot3d import Axes3D
    import cv2

    # Load YOLO configuration
    yolo_weights = os.getenv('YOLO_WEIGHTS')
    yolo_config = os.getenv('YOLO_CONFIG')
    coco_names = os.getenv('COCO_NAMES')
    tmp_output_dir = os.getenv('TMP_OUTPUT_DIR', '/tmp')

    try:
        if not os.path.exists(yolo_config):
            urllib.request.urlretrieve("https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg", yolo_config)
        if not os.path.exists(yolo_weights):
            urllib.request.urlretrieve("https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4.weights", yolo_weights)
        if not os.path.exists(coco_names):
            urllib.request.urlretrieve("https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names", coco_names)
    except Exception as e:
        raise RuntimeError(f"Failed to download YOLO files: {e}")

    net = cv2.dnn.readNetFromDarknet(yolo_config, yolo_weights)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    with open(coco_names, 'r') as f:
        classes = [line.strip() for line in f.readlines()]

    kafka_server = os.getenv('KAFKA_BOOTSTRAP_SERVER')
    image_topic = os.getenv('IMAGE_TOPIC')
    results_topic = os.getenv('RESULTS_TOPIC')

    consumer = KafkaConsumer(
        image_topic,
        bootstrap_servers=[kafka_server],
        auto_offset_reset='earliest',
        consumer_timeout_ms=10000
    )

    producer = KafkaProducer(
        bootstrap_servers=kafka_server,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    heatmap_size = (100, 100)
    heatmap = np.zeros(heatmap_size)

    for msg in consumer:
        img_bytes = msg.value
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        frame = np.array(img)
        height, width, _ = frame.shape

        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        outputs = net.forward(output_layers)

        detections = []
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if classes[class_id] == 'person' and confidence > 0.5:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    x = int((center_x / width) * heatmap_size[1])
                    y = int((center_y / height) * heatmap_size[0])
                    heatmap[y, x] += 1
                    detections.append({
                        'class': classes[class_id],
                        'confidence': float(confidence),
                        'center': {'x': center_x, 'y': center_y}
                    })

        result = {
            'frame_dimensions': {'width': width, 'height': height},
            'detections': detections
        }
        producer.send(results_topic, result)
        producer.flush()
        break

    consumer.close()

    # Save 2D heatmap
    plt.figure(figsize=(8, 6))
    plt.imshow(heatmap, cmap='hot', interpolation='nearest')
    plt.title('2D Crowd Heatmap')
    plt.xlabel('Grid X')
    plt.ylabel('Grid Y')
    plt.colorbar(label='Detection Count')
    plt.savefig(os.path.join(tmp_output_dir, '2d_heatmap.png'))
    plt.close()

    # Save 3D heatmap
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    X = np.arange(0, heatmap_size[1])
    Y = np.arange(0, heatmap_size[0])
    X, Y = np.meshgrid(X, Y)
    ax.plot_surface(X, Y, heatmap, cmap='hot')
    ax.set_title('3D Crowd Heatmap')
    ax.set_xlabel('Grid X')
    ax.set_ylabel('Grid Y')
    ax.set_zlabel('Detection Count')
    plt.savefig(os.path.join(tmp_output_dir, '3d_heatmap.png'))
    plt.close()

# Define DAG
with DAG(
    dag_id='crowd_heatmap_generation',
    default_args=default_args,
    start_date=datetime(2025, 4, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    generate_heatmap_task = PythonVirtualenvOperator(
        task_id='generate_crowd_heatmap',
        python_callable=process_image_blob_and_generate_heatmap,
        requirements=['opencv-python', 'matplotlib', 'numpy', 'kafka-python', 'Pillow'],
        system_site_packages=True,
        env_vars=ENV_VARS
    )

    generate_heatmap_task
