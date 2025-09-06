#include <Arduino_LSM6DS3.h>

// Constants for boundary limits
const float X_BOUNDARY_MIN = -90.0;  // Minimum boundary limit for X-axis
const float X_BOUNDARY_MAX = 90.0;   // Maximum boundary limit for X-axis
const float Y_BOUNDARY_MIN = -90.0;  // Minimum boundary limit for Y-axis
const float Y_BOUNDARY_MAX = 90.0;   // Maximum boundary limit for Y-axis

// Variables for data logging
unsigned long previousMillis = 0;     // Stores the previous time for data logging
const long interval = 1000;           // Interval for data logging (1 second)

// Variables for player tracking
float x, y, z;                        // Accelerometer readings
float speed;                          // Calculated speed of movement
String direction;                     // Direction of movement

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    delay(100);
  }
  Serial.println("Started");

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU! Retrying...");
    delay(1000);
    if (!IMU.begin()) {
      Serial.println("Failed to initialize IMU!");
      while (1);
    }
  }

  Serial.print("Accelerometer sample rate = ");
  Serial.print(IMU.accelerationSampleRate());
  Serial.println("Hz");
}

void loop() {
  unsigned long currentMillis = millis();  // Get current time

  if (currentMillis - previousMillis >= interval) {
    // Update previous time for data logging
    previousMillis = currentMillis;

    // Read accelerometer data
    if (IMU.accelerationAvailable()) {
      IMU.readAcceleration(x, y, z);
      // Validate accelerometer readings
      if (isnan(x) || isnan(y) || isnan(z)) {
        Serial.println("Invalid accelerometer readings!");
        return;
      }
    } else {
      // Handle IMU read failure
      Serial.println("Failed to read accelerometer data!");
      return;
    }

    // Calculate speed using magnitude of acceleration
    speed = sqrt(x * x + y * y + z * z);

    // Determine direction based on sign of acceleration
    if (x > 0.1) {
      direction = "Right";
    } else if (x < -0.1) {
      direction = "Left";
    } else if (y > 0.1) {
      direction = "Down";
    } else if (y < -0.1) {
      direction = "Up";
    } else {
      direction = "Stationary";
    }

    // Check for boundary crossing
    if (x < X_BOUNDARY_MIN || x > X_BOUNDARY_MAX || y < Y_BOUNDARY_MIN || y > Y_BOUNDARY_MAX) {
      // Boundary crossed, trigger event
      Serial.println("Boundary crossed!");
      // Add additional actions or alerts for boundary crossing here
    }

    // Log data
    Serial.print("Speed: ");
    Serial.print(speed);
    Serial.print(" Direction: ");
    Serial.println(direction);
  }
}
