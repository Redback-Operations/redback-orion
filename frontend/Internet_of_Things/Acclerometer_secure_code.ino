#include <Arduino_LSM6DS3.h>
#include <Adafruit_SleepyDog.h>

// Constants for boundary limits
const float X_BOUNDARY_MIN = -90.0;
const float X_BOUNDARY_MAX = 90.0;
const float Y_BOUNDARY_MIN = -90.0;
const float Y_BOUNDARY_MAX = 90.0;

// Constants for serial communication and timing
const int BAUD_RATE = 9600;
const long LOGGING_INTERVAL = 1000;
const float ACCELERATION_THRESHOLD = 0.1;

// Constants for retry mechanism
const int MAX_RETRIES = 3;
const int RETRY_DELAY = 1000;

// Variables for data logging
unsigned long previousMillis = 0;

// Variables for player tracking
float x, y, z;
float speed;
String direction;

void setup() {
  Serial.begin(BAUD_RATE);
  while (!Serial) {
    delay(100);
  }
  Serial.println("Started");

  // Initialize the watchdog timer with a 4-second timeout
  Watchdog.enable(4000);

  int retryCount = 0;
  while (!IMU.begin()) {
    Serial.println("Failed to initialize IMU! Retrying...");
    delay(RETRY_DELAY);
    retryCount++;
    if (retryCount >= MAX_RETRIES) {
      Serial.println("Failed to initialize IMU after multiple attempts.");
      return;  // Exit setup if the IMU cannot be initialized after retries
    }
  }

  Serial.print("Accelerometer sample rate = ");
  Serial.print(IMU.accelerationSampleRate());
  Serial.println(" Hz");
}

void loop() {
  Watchdog.reset();  // Regularly reset the watchdog timer to prevent it from resetting the system

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= LOGGING_INTERVAL) {
    previousMillis = currentMillis;

    if (IMU.accelerationAvailable()) {
      IMU.readAcceleration(x, y, z);

      if (isnan(x) || isnan(y) || isnan(z)) {
        Serial.println("Invalid accelerometer readings!");
        return;
      }

      speed = sqrt(x * x + y * y + z * z);

      if (x > ACCELERATION_THRESHOLD) {
        direction = "Right";
      } else if (x < -ACCELERATION_THRESHOLD) {
        direction = "Left";
      } else if (y > ACCELERATION_THRESHOLD) {
        direction = "Down";
      } else if (y < -ACCELERATION_THRESHOLD) {
        direction = "Up";
      } else {
        direction = "Stationary";
      }

      if (x < X_BOUNDARY_MIN || x > X_BOUNDARY_MAX || y < Y_BOUNDARY_MIN || y > Y_BOUNDARY_MAX) {
        Serial.println("Boundary crossed!");
      }

      Serial.print("Speed: ");
      Serial.print(speed);
      Serial.print(" Direction: ");
      Serial.println(direction);
    } else {
      Serial.println("Failed to read accelerometer data!");
    }
  }
}
