// sensorSchema.js
const mongoose = require('mongoose');

const SensorSchema = new mongoose.Schema({
  id: Number,
  name: String,
  address: String,
  time: Date,
  distance: Number
});

module.exports = mongoose.model('Sensor', SensorSchema);
