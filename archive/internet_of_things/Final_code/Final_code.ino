//Bhumika gave the acceleromter code and she initialised the variables for her part. 
//Sohil gave us the oximeter code and Informed me about the connections of the code with initialisation required at the specified locations. 
//Mayank gave me the heart rate code and also i had issue with his code, so he taught me some things about the print function and told me where the heart rate is actually stored in the index, placed his function in this code 
//Ishaan worked on combining the code, making functions for each sensor and then updating it seperately. Set the time intervals as 5 seconds for all but 1 second for heart rate as BLE gets disconnected if we make it wait too long. Solved the issue of getting too much of one sensor data in the output to make it easier to understand and fucntion. 


#include <Arduino_LSM6DS3.h>
#include <ArduinoBLE.h>
#include <TinyGPS++.h>
#include "DFRobot_BloodOxygen_S.h"

// Kalman Filter Class Definition
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

// Constants and Variable Definitions
const float ACC_THRESHOLD = 9.81 * 4; // 4g acceleration threshold
const float HIGH_ACCELERATION_THRESHOLD = 3.0; // High acceleration threshold in m/s^2
const long INTERVAL = 5000; // Data logging interval (1 second)
const long BLE_INTERVAL = 1000; // Interval for BLE updates
const long GPS_INTERVAL = 5000; // Interval for GPS updates
const int EARTH_RADIUS = 6371000; // Earth radius in meters

// Sensor instances and other global variables
TinyGPSPlus gps;
DFRobot_BloodOxygen_S_I2C MAX30102(&Wire, 0x57);
KalmanFilter filterX(0.01, 0.1, 1.0, 0);
KalmanFilter filterY(0.01, 0.1, 1.0, 0);
KalmanFilter filterZ(0.01, 0.1, 1.0, 0);
unsigned long previousMillis = 0, previousUpdateTime = 0, previousHeartRateTime = 0, previousGPSUpdateTime = 0;
float x, y, z; // Raw accelerometer readings
float filteredX, filteredY, filteredZ; // Filtered accelerometer readings
BLECharacteristic characteristic; // Global BLE characteristic variable
double previousLat = 0.0, previousLon = 0.0; // Previous GPS coordinates

// Function Declarations
double toRadians(double degree);
double haversine(double lat1, double lon1, double lat2, double lon2);
void initializeBLE();
void discoverAndConnect();
void printData(const unsigned char data[], int length);
String determineDirection(float x, float y, float z);
void updateGPS();

void setup() {
    Serial.begin(115200);
    Serial1.begin(9600);
    while (!Serial); // Wait for serial port to connect

    // Initialize sensors
    if (!IMU.begin()) {
        Serial.println("Failed to initialize IMU sensor!");
        while (1); // Halt if sensor initialization fails
    }
    Wire.begin();
    MAX30102.begin();
    initializeBLE();

    Serial.println("Multi-Sensor Tracking Initialized");
}

void loop() {
    unsigned long currentMillis = millis();

    // Accelerometer and Kalman filter processing
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
            float acceleration = sqrt(filteredX * filteredX + filteredY * filteredY + filteredZ * filteredZ);
            String direction = determineDirection(filteredX, filteredY, filteredZ);
            String accelerationAlert = (acceleration > HIGH_ACCELERATION_THRESHOLD) ? "Alert: High Acceleration Detected!" : "No Alert";
            Serial.print(acceleration, 2); // Ensure acceleration is printed with two decimal places
            Serial.print("\t");
            Serial.print(direction);
            Serial.print("\t");
            Serial.println(accelerationAlert);
        } else {
            Serial.println("Failed to read accelerometer data!");
        }
    }

    // BLE and Blood Oxygen sensor processing
    discoverAndConnect();
    BLE.poll(); // Poll for BLE events
    if (currentMillis - previousUpdateTime >= BLE_INTERVAL) {
        previousUpdateTime = currentMillis;
        if (characteristic.valueUpdated()) {
            printData(characteristic.value(), characteristic.valueLength());
        }
    }

    // GPS processing
    updateGPS();
}

double toRadians(double degree) {
    return degree * PI / 180.0;
}

double haversine(double lat1, double lon1, double lat2, double lon2) {
    double dLat = toRadians(lat2 - lat1);
    double dLon = toRadians(lon2 - lon1);
    double a = sin(dLat / 2) * sin(dLat / 2) + cos(toRadians(lat1)) * cos(toRadians(lat2)) * sin(dLon / 2) * sin(dLon / 2);
    double c = 2 * atan2(sqrt(a), sqrt(1 - a));
    return EARTH_RADIUS * c;
}

void initializeBLE() {
    Serial.println("Step 2: Initializing BLE");

    if (!BLE.begin()) {
        Serial.println("Failed to initialize BLE!");
        while (1); // Halt if initialization fails
    }

    Serial.println("BLE initialization successful, starting scan for service UUIDs...");
    BLE.scanForUuid("180D"); // Change to your required service UUID
}

void discoverAndConnect() {
    BLEDevice peripheral = BLE.available();

    if (peripheral) {
        Serial.println("Found a device, checking if it matches the required criteria...");
        Serial.print("Device Name: ");
        Serial.println(peripheral.localName());

        if (peripheral.localName() == "TICKR 0A5B") { // Check for specific device by name
            Serial.println("Device matches, attempting to connect...");
            BLE.stopScan();

            if (peripheral.connect()) {
                Serial.println("Connected successfully, discovering attributes...");

                if (peripheral.discoverAttributes()) {
                    Serial.println("Attributes discovered successfully.");

                    BLEService service = peripheral.service("180D");
                    if (service) {
                        characteristic = service.characteristic("2A37");
                        if (characteristic) {
                            characteristic.subscribe();
                            Serial.println("Subscription successful, ready to receive data...");
                        } else {
                            Serial.println("Characteristic '2A37' not found.");
                        }
                    } else {
                        Serial.println("Service '180D' not found.");
                    }
                } else {
                    Serial.println("Failed to discover attributes.");
                    peripheral.disconnect();
                }
            } else {
                Serial.println("Failed to connect.");
            }
        } else {
            Serial.println("Device does not match required criteria, continuing scan...");
        }
    }
}

void printData(const unsigned char data[], int length) {
    for (int i = 0; i < length; i++) {
        if (i == 1) { // Assuming data format where second byte is heart rate
            unsigned long currentTime = millis();
            unsigned char heartRate = data[i];

            // Update and print heart rate at intervals
            if (currentTime - previousHeartRateTime >= 5000) {
                previousHeartRateTime = currentTime;
                Serial.print("Heart Rate (BPM): ");
                Serial.println(heartRate);

                // Also read and print oximeter data
                MAX30102.getHeartbeatSPO2();
                Serial.print("SPO2: ");
                Serial.print(MAX30102._sHeartbeatSPO2.SPO2);
                Serial.println("%");
            }
        }
    }
}

String determineDirection(float x, float y, float z) {
    // Create a string that represents the direction vector with each component rounded to two decimal places
    return String(x, 2) + "i " + String(y, 2) + "j " + String(z, 2) + "k";
}

void updateGPS() {
    unsigned long currentMillis = millis();
    if (currentMillis - previousGPSUpdateTime >= GPS_INTERVAL) {
        previousGPSUpdateTime = currentMillis;
        while (Serial1.available() > 0) {
            char c = Serial1.read();
            //Serial.print(c); // Print raw GPS data for debugging
            if (gps.encode(c)) {
                if (gps.location.isValid()) {
                    double currentLat = gps.location.lat();
                    double currentLon = gps.location.lng();
                    // Serial.print("Current Lat: "); Serial.println(currentLat, 6);
                    // Serial.print("Current Lon: "); Serial.println(currentLon, 6);
                    double distance = haversine(previousLat, previousLon, currentLat, currentLon);
                    if(distance>0){
                      Serial.print("Distance (m): ");
                      Serial.println(distance);
                      previousLat = currentLat;
                      previousLon = currentLon;
                    }
                } else {
                    Serial.println("GPS location is not valid.");
                }
            }
        }
    }
}

//final
