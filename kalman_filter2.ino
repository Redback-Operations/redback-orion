#include <Arduino_LSM6DS3.h>

// Define a class for the Kalman filter
class KalmanFilter {
private:
    float q; // process noise covariance
    float r; // measurement noise covariance
    float x; // value
    float p; // estimation error covariance
    float k; // kalman gain

public:
    KalmanFilter(float process_noise, float sensor_noise, float estimated_error, float initial_value) {
        /* Initialize Kalman filter variables. */
        q = process_noise;
        r = sensor_noise;
        p = estimated_error;
        x = initial_value;
    }

    float update(float measurement) {
        /* Prediction update */
        p = p + q;

        /* Measurement update */
        k = p / (p + r);
        x = x + k * (measurement - x);
        p = (1 - k) * p;

        return x;
    }
};

// Constants for boundary limits
const float X_BOUNDARY_MIN = -90.0;  // Minimum boundary limit for X-axis
const float X_BOUNDARY_MAX = 90.0;   // Maximum boundary limit for X-axis
const float Y_BOUNDARY_MIN = -90.0;  // Minimum boundary limit for Y-axis
const float Y_BOUNDARY_MAX = 90.0;   // Maximum boundary limit for Y-axis

// Kalman Filter instances for each axis
KalmanFilter filterX(0.01, 0.1, 1.0, 0); // process noise, measurement noise, estimated error, initial value
KalmanFilter filterY(0.01, 0.1, 1.0, 0);
KalmanFilter filterZ(0.01, 0.1, 1.0, 0);

// Variables for data logging
unsigned long previousMillis = 0;
const long interval = 1000;  // Interval for data logging (1 second)

// Variables for player tracking
float x, y, z;  // Raw accelerometer readings
float filteredX, filteredY, filteredZ;  // Filtered accelerometer readings

void setup() {
  Serial.begin(9600);
  while (!Serial);  // Wait for the serial port to connect
  Serial.println("Player Tracking Initialized");

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);  // Halt if sensor fails to initialize
  }

  Serial.print("Accelerometer sample rate = ");
  Serial.print(IMU.accelerationSampleRate());
  Serial.println(" Hz");
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    if (IMU.accelerationAvailable()) {
      IMU.readAcceleration(x, y, z);
      
      // Apply Kalman filter to accelerometer readings
      filteredX = filterX.update(x);
      filteredY = filterY.update(y);
      filteredZ = filterZ.update(z);

      // Calculate activity intensity using magnitude of filtered acceleration
      float activityIntensity = sqrt(filteredX * filteredX + filteredY * filteredY + filteredZ * filteredZ);

      Serial.print("Filtered Activity Intensity: ");
      Serial.print(activityIntensity);
      Serial.println(" m/s^2");

      // Output additional processing based on filtered values
    } else {
      Serial.println("Failed to read accelerometer data!");
    }
  }
}
