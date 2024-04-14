import paho.mqtt.client as mqtt
from picamera import PiCamera
from time import sleep
from io import BytesIO

# MQTT Settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/camera"

# Setup camera
camera = PiCamera()
camera.resolution = (1024, 768)

# Connect to MQTT Broker
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def capture_image():
    stream = BytesIO()
    camera.start_preview()
    sleep(2)  # Camera warm-up time
    camera.capture(stream, 'jpeg')
    stream.seek(0)  # Rewind the stream to the beginning so we can read its content
    return stream.read()

def publish_image():
    image_data = capture_image()
    client.publish(MQTT_TOPIC, image_data)

publish_image()
client.disconnect()
