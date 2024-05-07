import paho.mqtt.client as mqtt
from pymongo import MongoClient

# MongoDB Settings
mongo_client = MongoClient(
    'mongodb://localhost:27017/',
    ssl=True,
    ssl_ca_certs="/path/to/ca-certificates.crt",
    ssl_certfile="/path/to/client-cert.pem",
    ssl_keyfile="/path/to/client-key.pem"
)
db = mongo_client.sensor_data
collection = db.readings

# MQTT Settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

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

client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Blocking call that processes network traffic, dispatches callbacks, and handles reconnecting.
client.loop_forever()
