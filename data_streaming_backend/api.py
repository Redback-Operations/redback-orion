import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from kafka import KafkaProducer
from PIL import Image
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timezone
from kafka import KafkaConsumer
from uuid import uuid4
from fastapi import Form

app = FastAPI()

# Kafka configuration
KAFKA_TOPIC = "heatmap"
KAFKA_SERVER = os.getenv('KAFKA_SERVER')
DAGS_UPLOAD_FOLDER = os.getenv('DAGS_UPLOAD_FOLDER', './uploaded_dags')

# Airflow configuration
AIRFLOW_BASE_URL = os.getenv('AIRFLOW_BASE_URL')
AIRFLOW_LOGIN = {
    "username": os.getenv('USERNAME'),
    "password": os.getenv('PASSWORD')
}
DAG_ID = "object_detection_single_task"

def compress_image_bytes(file: UploadFile, quality=50) -> bytes:
    """Compress uploaded image and return bytes."""
    img = Image.open(file.file)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=quality, optimize=True)
    return img_bytes.getvalue()

def send_to_kafka(image_bytes: bytes,topic:str=KAFKA_TOPIC):
    """Send compressed image to Kafka."""
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: v
    )
    future = producer.send(topic, image_bytes)
    producer.flush(timeout=10)
    return future.get(timeout=10)  # Wait for confirmation

def trigger_airflow_dag(dag_id):
    """Trigger Airflow DAG using session authentication."""
    session = requests.Session()
    login_url = f"{AIRFLOW_BASE_URL}/login/"
    
    # Step 1: Get CSRF token
    resp = session.get(login_url)
    if "csrf_token" in resp.text:
        soup = BeautifulSoup(resp.text, "html.parser")
        token = soup.find("input", {"name": "csrf_token"})["value"]
        AIRFLOW_LOGIN["csrf_token"] = token

    resp = session.post(login_url, data=AIRFLOW_LOGIN)
    if "DAGs" not in resp.text:
        raise Exception("Airflow login failed!")

    # Step 2: Trigger DAG
    trigger_url = f"{AIRFLOW_BASE_URL}/api/v1/dags/{dag_id}/dagRuns"
    dt = datetime.now(timezone.utc).replace(tzinfo=timezone.utc)
    payload = {
        "conf": {},
        "dag_run_id": f"run_{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.')}",
        "logical_date": dt.strftime('%Y-%m-%dT%H:%M:%S.') + f'{int(dt.microsecond / 1000):03d}Z',
        "note": "triggered via API"
    }
    headers = {"Content-Type": "application/json"}
    response = session.post(trigger_url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"DAG trigger failed: {response.text}")
    return response.json()

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), dag_id: str = DAG_ID):
    try:
        KAFKA_TOPIC = "image_blob_topic" if dag_id == 'object_detection_single_task' else 'heatmap'
        RESULT_TOPIC = "results_topic" if dag_id == 'object_detection_single_task' else 'heatmap_results'

        # Compress image and send to Kafka
        compressed_bytes = compress_image_bytes(file)
        kafka_result = send_to_kafka(compressed_bytes, KAFKA_TOPIC)

        # Trigger Airflow DAG
        airflow_result = trigger_airflow_dag(dag_id)

        # Wait for DAG run to complete and read JSON from Kafka result topic
        consumer = KafkaConsumer(
            RESULT_TOPIC,
            bootstrap_servers=KAFKA_SERVER,
            auto_offset_reset='latest',
            enable_auto_commit=False,
            group_id=f'result_consumer_group_{uuid4()}',
            value_deserializer=lambda x: x.decode('utf-8')
        )

        for message in consumer:
            consumer.close()
            return {
                "status": "success",
                "kafka": {
                    "topic": kafka_result.topic,
                    "result_topic": RESULT_TOPIC,
                    "partition": kafka_result.partition,
                    "offset": kafka_result.offset,
                },
                "airflow": airflow_result,
                "result": message.value
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/trigger-test-kafka-dag/")
def trigger_test_kafka_dag():
    """Trigger the test_kafka_in_virtualenv_dag DAG via Airflow API and wait for Kafka output."""
    try:
        session = requests.Session()
        login_url = f"{AIRFLOW_BASE_URL}/login/"
        
        # Get CSRF token
        resp = session.get(login_url)
        if "csrf_token" in resp.text:
            soup = BeautifulSoup(resp.text, "html.parser")
            token = soup.find("input", {"name": "csrf_token"})["value"]
            AIRFLOW_LOGIN["csrf_token"] = token

        resp = session.post(login_url, data=AIRFLOW_LOGIN)
        if "DAGs" not in resp.text:
            raise HTTPException(status_code=500, detail="Airflow login failed!")

        # Trigger DAG
        dag_id = "test_kafka_in_virtualenv_dag"
        trigger_url = f"{AIRFLOW_BASE_URL}/api/v1/dags/{dag_id}/dagRuns"
        payload = {
            "dag_run_id": f"run_{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.')}",
            "logical_date": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.') + f'{int(datetime.now(timezone.utc).microsecond / 1000):03d}Z',
            "note": "Test trigger for Kafka virtualenv DAG"
        }

        headers = {"Content-Type": "application/json"}
        response = session.post(trigger_url, json=payload, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"DAG trigger failed: {response.text}")

        # Wait for Kafka output
        consumer = KafkaConsumer(
            'kafka_test',
            bootstrap_servers=KAFKA_SERVER,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='test_kafka_group',
            value_deserializer=lambda x: x.decode('utf-8')
        )

        for message in consumer:
            consumer.close()
            return {
                "status": "DAG triggered and Kafka message received",
                "dag_id": dag_id,
                "kafka_message": message.value
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/")
def read_root():
    return {"message": "Welcome to the Image Upload API. Use /upload/ to upload an image."}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "API is running."}

@app.get("/health-kafka")
def health_check_kafka():
    """Health check for Kafka connection."""
    try:
        producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
        producer.close()
        return {"status": "ok", "message": "Kafka connection is healthy."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kafka connection failed: {str(e)}")
    
@app.get("/health-airflow")
def health_check_airflow():
    """Health check for Airflow connection."""
    try:
        response = requests.get(f"{AIRFLOW_BASE_URL}/health")
        if response.status_code == 200:
            return {"status": "ok", "message": "Airflow connection is healthy."}
        else:
            raise HTTPException(status_code=500, detail="Airflow connection failed.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Airflow connection failed: {str(e)}")

@app.post("/upload-dag/")
async def upload_dag(file: UploadFile = File(...), dag_name: str = Form(...)):
    try:
        if not os.path.exists(DAGS_UPLOAD_FOLDER):
            os.makedirs(DAGS_UPLOAD_FOLDER)
        dag_filename = f"{dag_name}.py"
        dag_path = os.path.join(DAGS_UPLOAD_FOLDER, dag_filename)
        with open(dag_path, "wb") as f:
            content = await file.read()
            f.write(content)
        return {"status": "success", "message": f"DAG '{dag_name}' uploaded successfully.", "path": dag_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload DAG: {str(e)}")