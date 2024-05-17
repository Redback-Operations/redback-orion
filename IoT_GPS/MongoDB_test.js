// At the very beginning of your script
process.env.TZ = 'Australia/Melbourne';

// Load environment variables from .env file
require('dotenv').config();

// Import necessary modules
const { SerialPort } = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');
const express = require('express');
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const Sensor = require('./sensorSchema'); // Ensure this path is correct
const mqtt = require('mqtt');

// Initialize Express app
const app = express();
const port1 = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

// CORS middleware
app.use(function (req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

// Connect to MongoDB using the connection string from the environment variables
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
}).then(() => {
  console.log('Connected to MongoDB');
}).catch((err) => {
  console.error('Error connecting to MongoDB', err);
});

// MQTT Broker Settings
const MQTT_BROKER = process.env.MQTT_BROKER; // Local MQTT broker
const MQTT_TOPIC = process.env.MQTT_TOPIC;

// Connect to MQTT Broker
const client = mqtt.connect(MQTT_BROKER);

client.on('connect', () => {
  console.log('Connected to MQTT Broker');
});

// Serial port setup
const port = new SerialPort({ path: process.env.SERIAL_PORT, baudRate: 9600 }, false);
const parser = port.pipe(new ReadlineParser({ delimiter: '\r\n' }));

// Function to handle incoming data from the serial port
parser.on('data', async data => {
  console.log("Received data from serial port:", data);
  // Assuming the data format is "Distance: <numeric_value>"
  const dataParts = data.split("Distance: ");
  if (dataParts.length > 1) {
    const distanceStr = dataParts[1].trim(); // Trim any leading/trailing whitespace
    const distance = parseFloat(distanceStr); // Attempt to parse the string to a number

    if (isNaN(distance)) {
      console.error("Failed to parse distance:", distanceStr);
      return; // Skip saving to MongoDB if parsing fails
    }

    try {
      const newSensor = new Sensor({
        id: 0,
        name: "GPS Sensor",
        address: "Your address here", // Update with your address
        time: Date.now(),
        distance: distance
      });

      await newSensor.save();
      console.log("Distance data added to MongoDB");

      // Publish the distance to MQTT
      client.publish(MQTT_TOPIC, `Distance: ${distance}`);
      console.log(`Published: Distance: ${distance} to topic ${MQTT_TOPIC}`);
    } catch (err) {
      console.log(err);
    }
  } else {
    console.error("Unexpected data format:", data);
  }
});

// Start the Express server
app.listen(port1, () => {
  console.log(`Listening on port ${port1}`);
});
