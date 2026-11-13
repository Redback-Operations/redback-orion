import os
import paho.mqtt.client as mqtt
from pymongo import MongoClient
import ssl

# Load MongoDB credentials from environment variables
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
MONGODB_PORT = int(os.getenv("MONGODB_PORT", 27017))
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "mydatabase")

# Construct MongoDB URI with SSL options
MONGODB_URI = (
    f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DATABASE}"
    "?ssl=true&ssl_cert_reqs=CERT_NONE"
)

# MongoDB Settings
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client.sensor_data
collection = db.readings

# MQTT Settings
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("sensor/#")  # Subscribe to all topics starting with sensor/

def on_message(client, userdata, msg):
    print(f"Received message from {msg.topic}: {msg.payload.decode()}")
    # Insert into MongoDB
    collection.insert_one({"topic": msg.topic, "data": msg.payload.decode()})

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Set up SSL/TLS for MQTT connection
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Blocking call that processes network traffic, dispatches callbacks, and handles reconnecting.
client.loop_forever()
