// app.js

// MongoDB setup
const mongoose = require('mongoose');
const Sensor = require('./sensorSchema'); // Import the schema

mongoose.connect('mongodb://localhost/GY-Neo-6M', { useNewUrlParser: true, useUnifiedTopology: true });

// Function to store data in MongoDB
function storeDataInMongoDB(lat1, lon1, lat2, lon2, distance) {
  const sensordata = {
    id: 0,
    name: "GPS Sensor",
    address: "Your address here", // Update with your address
    time: Date.now(),
    lat1: lat1,
    lon1: lon1,
    lat2: lat2,
    lon2: lon2,
    distance: distance
  };

  const newSensor = new Sensor(sensordata);

  newSensor.save().then(doc => {
    console.log(doc);
  }).catch(err => {
    console.error(err);
  });
}

// Serial port setup
const SerialPort = require('serialport');
const Readline = require('@serialport/parser-readline');
const port = new SerialPort('COMx', { baudRate: 9600 }); // Update COMx with your Arduino's COM port
const parser = port.pipe(new Readline({ delimiter: '\r\n' }));

// Reading data from Arduino and storing in MongoDB
parser.on('data', data => {
  const dataArray = data.split(','); // Assuming data is sent as "lat1,lon1,lat2,lon2,distance"
  const lat1 = parseFloat(dataArray[0]);
  const lon1 = parseFloat(dataArray[1]);
  const lat2 = parseFloat(dataArray[2]);
  const lon2 = parseFloat(dataArray[3]);
  const distance = parseFloat(dataArray[4]);
  
  storeDataInMongoDB(lat1, lon1, lat2, lon2, distance);
});
