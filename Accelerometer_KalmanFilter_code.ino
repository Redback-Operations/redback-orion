#include <Arduino_LSM6DS3.h>

class KalmanFilter {
private:
    float q; // process noise covariance
    float r; // measurement noise covariance
    float x; // value
    float p; // estimation error covariance
    float k; // kalman gain

public:
    KalmanFilter(float process_noise, float sensor_noise, float estimated_error, float initial_value) {
        q = process_noise;
        r = sensor_noise;
        p = estimated_error;
        x = initial_value;
    }

    float update(float measurement) {
        p += q; // Prediction update
        k = p / (p + r); // Measurement update
        x += k * (measurement - x);
        p *= (1 - k);
        return x;
    }
};

const float ACC_THRESHOLD = 9.81 * 4; // 4g acceleration threshold
const float HIGH_SPEED_THRESHOLD = 2.0; // High speed threshold in m/s^2
const long INTERVAL = 1000; // Data logging interval (1 second)

KalmanFilter filterX(0.01, 0.1, 1.0, 0);
KalmanFilter filterY(0.01, 0.1, 1.0, 0);
KalmanFilter filterZ(0.01, 0.1, 1.0, 0);

unsigned long previousMillis = 0;
unsigned long messageCount = 0; // Simple timestamp increment
float x, y, z; // Raw accelerometer readings
float filteredX, filteredY, filteredZ; // Filtered accelerometer readings
float speed; // Calculated speed
String direction; // Direction of movement

void setup() {
    Serial.begin(9600);
    while (!Serial); // Wait for serial port to connect
    if (!IMU.begin()) {
        Serial.println("Failed to initialize IMU sensor!");
        while (1); // Halt if sensor initialization fails
    }
    Serial.println("Player Tracking Initialized");
}

void loop() {
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= INTERVAL) {
        previousMillis = currentMillis;
        if (IMU.accelerationAvailable()) {
            IMU.readAcceleration(x, y, z);
            if (abs(x) > ACC_THRESHOLD || abs(y) > ACC_THRESHOLD || abs(z) > ACC_THRESHOLD) {
                Serial.println("Warning: Acceleration data exceeds safety thresholds!");
                return;
            }
            filteredX = filterX.update(x);
            filteredY = filterY.update(y);
            filteredZ = filterZ.update(z);
            speed = sqrt(filteredX * filteredX + filteredY * filteredY + filteredZ * filteredZ);
            direction = determineDirection(filteredX, filteredY);
            String speedAlert = (speed > HIGH_SPEED_THRESHOLD) ? "Alert: High Speed Detected!" : "No Alert";
            String directionAlert = (direction == "Right Up") ? "Alert: Significant Right Upward Movement Detected!" : "No Alert";
            sendToSerial(messageCount, speed, direction, speedAlert, directionAlert);
        } else {
            Serial.println("Failed to read accelerometer data!");
        }
    }
}

String determineDirection(float x, float y) {
    String dir = "Stationary";
    if (x > 0.1) dir = "Right";
    else if (x < -0.1) dir = "Left";
    if (y > 0.1) dir += " Down";
    else if (y < -0.1) dir += " Up";
    return dir;
}

void sendToSerial(unsigned long count, float speed, String direction, String speedAlert, String directionAlert) {
    Serial.print(count);
    Serial.print("\t");
    Serial.print(speed, 2); // Print speed with two decimal places
    Serial.print("\t");
    Serial.print(direction);
    Serial.print("\t");
    Serial.print(speedAlert);
    Serial.print("\t");
    Serial.println(directionAlert);
}
