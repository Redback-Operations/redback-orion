import os
import tempfile
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator

# Default arguments
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Use OS-agnostic temp directory
tmp_dir = tempfile.gettempdir()
weights_file = os.path.join(tmp_dir, 'yolov8n.pt')

ENV_VARS = {
    'KAFKA_BOOTSTRAP_SERVER': os.getenv('KAFKA_BOOTSTRAP_SERVER', 'redback.it.deakin.edu.au:9092'),
    'IMAGE_TOPIC': 'image_blob_topic',
    'JSON_TOPIC': 'results_topic',
    'IMG_OUT_TOPIC': 'result_image_topic',
    'YOLO_WEIGHTS_PATH': weights_file
}

with DAG(
    dag_id='object_detection_single_task',
    default_args=default_args,
    start_date=datetime(2025, 4, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    def download_weights():
        import os
        from sahi.utils.ultralytics import download_model_weights
        weights_path = os.getenv('YOLO_WEIGHTS_PATH')
        if not os.path.exists(weights_path):
            download_model_weights(weights_path)

    download_weights_task = PythonVirtualenvOperator(
        task_id='download_weights',
        python_callable=download_weights,
        requirements=['sahi', 'ultralytics'],
        system_site_packages=True,
        env_vars=ENV_VARS
    )

    def consume_and_detect():
        import os, io, json
        from kafka import KafkaConsumer, KafkaProducer
        from sahi import AutoDetectionModel
        from sahi.predict import get_sliced_prediction
        from PIL import Image

        kafka_server = os.getenv('KAFKA_BOOTSTRAP_SERVER')
        image_topic = os.getenv('IMAGE_TOPIC')
        json_topic = os.getenv('JSON_TOPIC')
        img_topic = os.getenv('IMG_OUT_TOPIC')
        weights_path = os.getenv('YOLO_WEIGHTS_PATH')

        consumer = KafkaConsumer(
            image_topic,
            bootstrap_servers=[kafka_server],
            auto_offset_reset='earliest',
            consumer_timeout_ms=10000,
        )
        for msg in consumer:
            img_bytes = msg.value
            break
        else:
            raise RuntimeError('No image blob received from Kafka topic')

        img = Image.open(io.BytesIO(img_bytes))

        model = AutoDetectionModel.from_pretrained(
            model_type='yolov8',
            model_path=weights_path,
            confidence_threshold=0.3,
            device='cpu'
        )

        result = get_sliced_prediction(
            image=img,
            detection_model=model,
            slice_height=256,
            slice_width=256,
            overlap_height_ratio=0.2,
            overlap_width_ratio=0.2,
        )

        preds = [
            {
                'category_id': int(o.category.id),
                'category_name': o.category.name,
                'score': float(o.score.value),
                'bbox': {
                    'x_min': o.bbox.minx,
                    'y_min': o.bbox.miny,
                    'x_max': o.bbox.maxx,
                    'y_max': o.bbox.maxy
                }
            }
            for o in result.object_prediction_list
        ]
        json_payload = json.dumps(preds).encode('utf-8')

        producer = KafkaProducer(
            bootstrap_servers=kafka_server,
            value_serializer=lambda v: v
        )
        producer.send(json_topic, json_payload)
        producer.flush()

    consume_and_detect_task = PythonVirtualenvOperator(
        task_id='consume_and_detect',
        python_callable=consume_and_detect,
        requirements=['sahi', 'ultralytics', 'kafka-python', 'Pillow'],
        system_site_packages=True,
        env_vars=ENV_VARS
    )

    download_weights_task >> consume_and_detect_task
