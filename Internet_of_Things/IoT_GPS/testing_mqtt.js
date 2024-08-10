const fs = require('fs');
const csv = require('csv-parser');
const mqtt = require('mqtt');

// MQTT Broker Settings
const MQTT_BROKER = 'mqtt://redback.it.deakin.edu.au:1883/';
const MQTT_TOPIC = 'testing';

// Connect to MQTT Broker
const client = mqtt.connect(MQTT_BROKER);

client.on('connect', () => {
    console.log('Connected to MQTT Broker');

    // Read CSV File and Publish Data
    fs.createReadStream('data.csv')
        .pipe(csv())
        .on('data', (row) => {
            const payload = `${row.time},${row.HeartRate}`;
            client.publish(MQTT_TOPIC, payload);
            console.log(`Published: ${payload} to topic ${MQTT_TOPIC}`);
        })
        .on('end', () => {
            client.end();
        });
});
