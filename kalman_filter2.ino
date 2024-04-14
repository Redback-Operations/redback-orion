#include <Arduino_LSM6DS3.h>
#include <array>

// Include the Kalman library
#include <Kalman.h>

// Constants for boundary limits
const float X_BOUNDARY_MIN = -90.0;  // Minimum boundary limit for X-axis
const float X_BOUNDARY_MAX = 90.0;   // Maximum boundary limit for X-axis
const float Y_BOUNDARY_MIN = -90.0;  // Minimum boundary limit for Y-axis
const float Y_BOUNDARY_MAX = 90.0;   // Maximum boundary limit for Y-axis

// Variables for data logging
unsigned long previousMillis = 0;     // Stores the previous time for data logging
const long interval = 1000;           // Interval for data logging (1 second)

// Variables for player tracking
float x, y, z;                        // Raw accelerometer readings
float filteredX, filteredY;           // Filtered accelerometer readings
float speed;                          // Calculated speed of movement
String direction;                     // Direction of movement

// Kalman filter variables
Kalman<float, 2, 1> kalmanX;          // Kalman filter for X-axis
Kalman<float, 2, 1> kalmanY;          // Kalman filter for Y-axis

void setup() {
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Started");

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  // Initialize Kalman filters
  kalmanX.setProcessNoise(0.01);
  kalmanX.setMeasurementNoise(3);
  kalmanX.setSensorNoise(10);

  kalmanY.setProcessNoise(0.01);
  kalmanY.setMeasurementNoise(3);
  kalmanY.setSensorNoise(10);

  Serial.print("Accelerometer sample rate = ");
  Serial.print(IMU.accelerationSampleRate());
  Serial.println("Hz");
}

void loop() {
  unsigned long currentMillis = millis();  // Get current time

  if (currentMillis - previousMillis >= interval) {
    // Update previous time for data logging
    previousMillis = currentMillis;

    // Read raw accelerometer data
    if (IMU.accelerationAvailable()) {
      IMU.readAcceleration(x, y, z);
    }

    // Apply Kalman filter to accelerometer data
    float inputX[1] = {x};
    float inputY[1] = {y};
    kalmanX.updateEstimate(inputX);
    kalmanY.updateEstimate(inputY);

    // Get filtered values
    filteredX = kalmanX.getEstimate();
    filteredY = kalmanY.getEstimate();

    // Calculate speed using magnitude of filtered acceleration
    speed = sqrt(filteredX * filteredX + filteredY * filteredY);

    // Determine direction based on sign of filtered acceleration
    if (filteredX > 0.1) {
      direction = "Right";
    } else if (filteredX < -0.1) {
      direction = "Left";
    } else if (filteredY > 0.1) {
      direction = "Down";
    } else if (filteredY < -0.1) {
      direction = "Up";
    } else {
      direction = "Stationary";
    }

    // Check for boundary crossing
    if (filteredX < X_BOUNDARY_MIN || filteredX > X_BOUNDARY_MAX || filteredY < Y_BOUNDARY_MIN || filteredY > Y_BOUNDARY_MAX) {
      // Boundary crossed, trigger event
      Serial.println("Boundary crossed!");
    }

    // Log data
    Serial.print("Speed: ");
    Serial.print(speed);
    Serial.print(" Direction: ");
    Serial.println(direction);

    // Visualize movement on Serial Plotter
    Serial.print("X: ");
    Serial.print(filteredX);
    Serial.print("\tY: ");
    Serial.println(filteredY);
  }
}
