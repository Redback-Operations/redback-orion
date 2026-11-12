#include "DFRobot_BloodOxygen_S.h"

// Define the I2C address for the MAX30102 sensor
#define I2C_ADDRESS 0x57

// Create an instance of the DFRobot_BloodOxygen_S_I2C class for I2C communication
DFRobot_BloodOxygen_S_I2C MAX30102(&Wire, I2C_ADDRESS);

void setup()
{
  // Initialize serial communication at a baud rate of 115200
  Serial.begin(115200);

  // Attempt to initialize the MAX30102 sensor
  while (false == MAX30102.begin())
  {
    // If initialization fails, print an error message and wait for 1 second before retrying
    Serial.println("init fail!");
    delay(1000);
  }

  // If initialization is successful, print a success message
  Serial.println("init success!");

  // Print a message indicating that measurement is starting
  Serial.println("start measuring...");

  // Start collecting data from the sensor
  MAX30102.sensorStartCollect();
}

void loop()
{
  // Retrieve the heartbeat and SPO2 (blood oxygen saturation) data from the sensor
  MAX30102.getHeartbeatSPO2();

  // Print the SPO2 value to the serial monitor
  Serial.print("SPO2 is : ");
  Serial.print(MAX30102._sHeartbeatSPO2.SPO2);
  Serial.println("%");

  // The sensor updates the data every 4 seconds, so delay for 4 seconds before the next read
  delay(4000);

  // Uncomment the following lines if you want to stop the measurement
  // Serial.println("stop measuring...");
  // MAX30102.sensorEndCollect();
}
