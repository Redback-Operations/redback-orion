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
const float HIGH_ACCELERATION_THRESHOLD = 3.0; // High acceleration threshold in m/s^2
const long INTERVAL = 1000; // Data logging interval (1 second)

KalmanFilter filterX(0.01, 0.1, 1.0, 0);
KalmanFilter filterY(0.01, 0.1, 1.0, 0);
KalmanFilter filterZ(0.01, 0.1, 1.0, 0);

unsigned long previousMillis = 0;
float x, y, z; // Raw accelerometer readings
float filteredX, filteredY, filteredZ; // Filtered accelerometer readings
float acceleration; // Calculated acceleration
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
            acceleration = sqrt(filteredX * filteredX + filteredY * filteredY + filteredZ * filteredZ);
            direction = determineDirection(filteredX, filteredY, filteredZ);
            String accelerationAlert = (acceleration > HIGH_ACCELERATION_THRESHOLD) ? "Alert: High Acceleration Detected!" : "No Alert";
            String directionAlert = (direction == "0.03i 0.09j 0.96k" && acceleration > 4) ? "Alert: Significant Right Upward Movement Detected!" : "No Alert";
            sendToSerial(acceleration, direction, accelerationAlert, directionAlert);
        } else {
            Serial.println("Failed to read accelerometer data!");
        }
    }
}

String determineDirection(float x, float y, float z) {
    return String(x, 2) + "i " + String(y, 2) + "j " + String(z, 2) + "k";
}

void sendToSerial(float acceleration, String direction, String accelerationAlert, String directionAlert) {
    Serial.print(acceleration, 2); // Ensure acceleration is printed with two decimal places
    Serial.print("\t");
    Serial.print(direction);
    Serial.print("\t");
    Serial.print(accelerationAlert);
    Serial.print("\t");
    Serial.println(directionAlert);
}
