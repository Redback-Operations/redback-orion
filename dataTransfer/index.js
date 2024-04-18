const { SerialPort } = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');
const fs = require('fs');

// Set the correct COM port name and CSV file path
const portName = 'COM3';
const csvFilePath = '\data transfer\mayank_ll.csv';

// Create a writable stream to the CSV file
const csvStream = fs.createWriteStream(csvFilePath);

// Write the CSV header
csvStream.write('time,data values\n');

// Create a SerialPort instance
const port = new SerialPort(portName, { baudRate: 9600 });

// Create a Readline parser instance
const parser = port.pipe(new ReadlineParser({ delimiter: '\r\n' }));

// Event handler for errors
port.on('error', function (err) {
    console.error('Error:', err.message);
});

// Event handler for receiving data
parser.on('data', data => {
    const currentTime = new Date().toISOString(); // Generate the current time
    csvStream.write(`${currentTime},${data}\n`); // Write data to the CSV file
    console.log(`${currentTime} | ${data}`);
});
