const fs = require("fs");
const { SerialPort } = require("serialport");
const { ReadlineParser } = require("@serialport/parser-readline");
const createCsvWriter = require("csv-writer").createObjectCsvWriter;

// Function to initialize the CSV file with headers
function initializeCsv() {
  // Check if the CSV file exists and is not empty
  if (!fs.existsSync(csvFilePath) || fs.statSync(csvFilePath).size === 0) {
    console.log("Creating CSV file with headers.");
    csvWriter
      .writeRecords([]) // Empty record to initialize headers
      .then(() => console.log("CSV file initialized with headers."))
      .catch((err) => console.error("Failed to initialize CSV file:", err));
  } else {
    console.log("CSV file already exists and is not empty.");
  }
}

const csvFilePath = "Accelerometer_data.csv";
const csvWriter = createCsvWriter({
  path: csvFilePath,
  header: [
    { id: "timestamp", title: "Timestamp" },
    { id: "Acceleration", title: "Acceleration" },
    { id: "direction", title: "Direction" },
    { id: "AccelerationAlert", title: "Alert message for Acceleration" },
    { id: "directionAlert", title: "Alert message for direction" },
  ],
  append: true,
});

// Initialize the CSV file with headers before starting the serial port listener
initializeCsv();

const port = new SerialPort({ path: "COM17", baudRate: 9600 });
const parser = port.pipe(new ReadlineParser({ delimiter: "\n" }));

parser.on("data", (data) => {
  console.log(`Received data: ${data}`);
  const parsedData = parseData(data);
  if (parsedData) {
    csvWriter
      .writeRecords([parsedData])
      .then(() => console.log("Data appended to CSV file successfully"))
      .catch((err) => console.error("Error writing data to CSV file:", err));
  } else {
    console.error("Invalid data format received:", data);
  }
});

function parseData(dataString) {
  // Trimming the arrow '->' and any leading/trailing whitespace from the data string
  const trimmedString = dataString
    .substring(dataString.indexOf(">") + 2)
    .trim();
  console.log(`Trimmed data string: ${trimmedString}`);

  // Define the regex pattern to match the data format
  const regex =
    /^(?<Acceleration>\d+\.\d+)\t(?<direction>[^\t]+)\t(?<AccelerationAlert>No Alert|Alert: High Acceleration Detected!)\t(?<directionAlert>No Alert|Alert: Significant Right Upward Movement Detected!)$/;

  // Attempt to match the data string to the regex pattern
  const match = trimmedString.match(regex);
  if (match) {
    const { Acceleration, direction, AccelerationAlert, directionAlert } =
      match.groups;
    return {
      timestamp: new Date().toISOString(), // Generating a timestamp for the received data
      Acceleration,
      direction,
      AccelerationAlert,
      directionAlert,
    };
  } else {
    console.error("Data did not match the expected format:", trimmedString);
    return null;
  }
}
