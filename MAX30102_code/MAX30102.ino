#include <Wire.h>
#include "MAX30105.h" // This library is also used for MAX30102
#include "spo2_algorithm.h"

MAX30105 particleSensor;

uint32_t irBuffer[100]; // Infrared LED buffer
uint32_t redBuffer[100];  // Red LED buffer
int32_t bufferLength = 100; // Buffer length
int32_t spo2; // SPO2 value
int8_t validSPO2; // Indicator to show if the SPO2 calculation is valid
int32_t heartRate; // Heart rate value
int8_t validHeartRate; // Indicator to show if the heart rate calculation is valid

void setup() {
  Serial.begin(115200); // Start serial communication
  Serial.println("Initializing...");

  // Initialize the MAX30102 sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("Could not find a valid MAX30105 sensor, check wiring!");
    while (1);
  }

  particleSensor.setup(); // Configure with default settings
  // See the MAX30105/SparkFun library for configuration options

  Serial.println("MAX30102 Initialized");
}

void loop() {
  // Fill the buffers with samples
  for (int i = 0; i < bufferLength; i++) {
    while (particleSensor.available() == false) // Wait for a new sample
      particleSensor.check(); // Check the sensor for new data

    redBuffer[i] = particleSensor.getRed();
    irBuffer[i] = particleSensor.getIR();
    particleSensor.nextSample(); // Move to next sample
  }

  // Calculate heart rate and SpO2 after filling the buffer
  maxim_heart_rate_and_oxygen_saturation(irBuffer, bufferLength, redBuffer, &spo2, &validSPO2, &heartRate, &validHeartRate);

  // Output the results
  if (validHeartRate && validSPO2) {
    Serial.print("Heart Rate: ");
    Serial.print(heartRate);
    Serial.print(" bpm, SpO2: ");
    Serial.print(spo2);
    Serial.println("%");
  } else {
    Serial.println("Failed to compute valid heart rate/SpO2.");
  }

  delay(1000);
}
