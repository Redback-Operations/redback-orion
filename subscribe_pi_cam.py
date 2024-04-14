import paho.mqtt.client as mqtt
from pymongo import MongoClient

# MongoDB Settings
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client.sensor_data
collection = db.readings

# MQTT Settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("sensor/#")  # Subscribe to all topics starting with sensor/

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    # Insert into MongoDB
    collection.insert_one({"topic": msg.topic, "data": msg.payload})

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
client.loop_forever()
