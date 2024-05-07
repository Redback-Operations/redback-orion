import paho.mqtt.client as mqtt
from picamera import PiCamera
from time import sleep
from io import BytesIO
import os

# MQTT Settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/camera"

# Retrieve MQTT username and password from environment variables
MQTT_USERNAME = os.environ.get("MQTT_USERNAME")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD")

# Check if credentials are provided
if MQTT_USERNAME is None or MQTT_PASSWORD is None:
    raise ValueError("MQTT username or password not provided in environment variables")

# Setup camera
camera = PiCamera()
camera.resolution = (1024, 768)

# Connect to MQTT Broker
client = mqtt.Client()
client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def capture_image():
    try:
        stream = BytesIO()
        camera.start_preview()
        sleep(2)  # Camera warm-up time
        camera.capture(stream, 'jpeg')
        stream.seek(0)  # Rewind the stream to the beginning so we can read its content
        return stream.read()
    except Exception as e:
        print("Error capturing image:", e)
        return None  # Return None if an error occurs

def publish_image():
    image_data = capture_image()
    if image_data is not None:
        try:
            client.publish(MQTT_TOPIC, image_data)
        except Exception as e:
            print("Error publishing image:", e)

publish_image()
client.disconnect()
