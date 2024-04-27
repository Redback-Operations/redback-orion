#include "DFRobot_BloodOxygen_S.h" // Include library for Blood Oxygen sensor DFRobot

#define I2C_COMMUNICATION  // Define the communication type as I2C

#ifdef I2C_COMMUNICATION
#define I2C_ADDRESS    0x57 // Set the I2C address for the sensor
  DFRobot_BloodOxygen_S_I2C MAX30102(&Wire ,I2C_ADDRESS); // Create an instance of the sensor using I2C communication
#else
// If not using I2C, select the appropriate serial communication based on the board type
#if defined(ARDUINO_AVR_UNO) || defined(ESP8266)
SoftwareSerial mySerial(4, 5); // Create a software serial port for boards like UNO or ESP8266
DFRobot_BloodOxygen_S_SoftWareUart MAX30102(&mySerial, 9600);
#else
DFRobot_BloodOxygen_S_HardWareUart MAX30102(&Serial1, 9600); // Use hardware serial port for other boards
#endif
#endif

void setup()
{
  Serial.begin(115200); // Initialize serial communication at 115200 bps
  while (false == MAX30102.begin())
  {
    Serial.println("init fail!"); // Print initialization failure message
    delay(1000); // Wait for a second before retrying initialization
  }
  Serial.println("init success!"); // Print successful initialization message
  Serial.println("start measuring..."); // Indicate that measurements will start
  MAX30102.sensorStartCollect(); // Start data collection from the sensor
}

void loop()
{
  MAX30102.getHeartbeatSPO2(); // Retrieve the SPO2 data from the sensor
  Serial.print("SPO2 is : "); // Display SPO2 reading
  Serial.print(MAX30102._sHeartbeatSPO2.SPO2);
  Serial.println("%");
  Serial.print("Temperature value of the board is : "); // Display the temperature of the sensor board
  Serial.print(MAX30102.getTemperature_C());
  Serial.println(" ℃");
  delay(2000); // Delay for 2 seconds before repeating the measurements
}
