const { SerialPort } = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');
const fs = require('fs').promises; // Using fs.promises for async file operations
const path = require('path');

const portName = 'COM3';
const csvFilePath = path.join(__dirname, 'mayank_ll.csv');

async function main() {
    // Create a SerialPort instance
    const port = new SerialPort(portName, { baudRate: 9600 });

    // Create a Readline parser instance
    const parser = port.pipe(new ReadlineParser({ delimiter: '\r\n' }));

    // Create a writable stream to the CSV file
    const csvStream = fs.createWriteStream(csvFilePath);

    // Write the CSV header
    await csvStream.write('time,data values\n');

    // Event handler for errors
    port.on('error', function (err) {
        console.error('Error:', err.message);
    });

    // Initialize currentTime outside the data event handler
    const currentTime = new Date().toISOString();

    // Event handler for receiving data
    parser.on('data', async (data) => {
        try {
            // Check if the data is in the expected format
            if (data) {
                // Write data to the CSV file
                await csvStream.write(`${currentTime},${data}\n`);
                console.log(`${currentTime} | ${data}`);
            }
        } catch (error) {
            console.error('Error writing to CSV:', error);
        }
    });
}

main().catch(error => {
    console.error('Error:', error);
});
