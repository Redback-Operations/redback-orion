#include <ArduinoBLE.h>
#include <TinyGPS++.h>
#include <Arduino_LSM6DS3.h>

TinyGPSPlus gps;

#define EARTH_RADIUS 6371000 // in meters

// Function to convert degrees to radians
double toRadians(double degree) {
  return degree * PI / 180.0;
}

// Haversine formula to calculate distance between two points
double haversine(double lat1, double lon1, double lat2, double lon2) {
  double dLat = toRadians(lat2 - lat1);
  double dLon = toRadians(lon2 - lon1);
  double a = sin(dLat / 2) * sin(dLat / 2) + cos(toRadians(lat1)) * cos(toRadians(lat2)) * sin(dLon / 2) * sin(dLon / 2);
  double c = 2 * atan2(sqrt(a), sqrt(1 - a));
  return EARTH_RADIUS * c;
}

// Kalman Filter Class
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

// Function Declarations
void initializeBLE();
void discoverAndConnect();
void printData(const unsigned char data[], int length);
void printHeartRate(const unsigned char data[], int length);
void sendToSerial(unsigned long count, float speed, String direction, String speedAlert, String directionAlert, unsigned char heartRate, double distance);
String determineDirection(float x, float y);

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
  Serial1.begin(9600);
  while (!Serial);
  Serial.println("Step 1: Starting Service");
  initializeBLE();

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU sensor!");
    while (1); // Halt if sensor initialization fails
  }
  Serial.println("Player Tracking Initialized");
}

void loop() {
  discoverAndConnect();
  BLE.poll();  // Poll for BLE events and communication updates.
  
  // Accelerometer data and heart rate processing
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= INTERVAL) {
    previousMillis = currentMillis;
    // Accelerometer data processing
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

      // Read heart rate
      unsigned char heartRate;
      if (BLE.connected()) {
        BLEDevice peripheral = BLE.central();
        if (peripheral) {
          BLEService heartRateService = peripheral.service("180D");
          if (heartRateService) {
            BLECharacteristic heartRateCharacteristic = heartRateService.characteristic("2A37");
            if (heartRateCharacteristic) {
              if (heartRateCharacteristic.valueUpdated()) {
                heartRate = heartRateCharacteristic.value()[1]; // Assuming heart rate value is at index 1
              }
            }
          }
        }
      }

      // Read GPS coordinates
      double distance;
      while (Serial1.available() >= 0) {
        if (gps.encode(Serial1.read())) {
          if (gps.location.isValid()) {
            double currentLat = gps.location.lat();
            double currentLon = gps.location.lng();
            static double previousLat = 0.0;
            static double previousLon = 0.0;
            distance = haversine(previousLat, previousLon, currentLat, currentLon);
            // if (distance > 0) {
            //   Serial.print("Distance: ");
            //   Serial.println(distance);
            // }
            previousLat = currentLat;
            previousLon = currentLon;
            break;
          }
        }
      }

      sendToSerial(messageCount, speed, direction, speedAlert, directionAlert, heartRate, distance);
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

void sendToSerial(unsigned long count, float speed, String direction, String speedAlert, String directionAlert, unsigned char heartRate, double distance) {
  Serial.print(count);
  Serial.print("\t");
  Serial.print(speed, 2); // Print speed with two decimal places
  Serial.print("\t");
  Serial.print(direction);
  Serial.print("\t");
  Serial.print(speedAlert);
  Serial.print("\t");
  Serial.print(directionAlert);
  Serial.print("\t");
  Serial.print("Heart Rate Value (BPM) = ");
  Serial.print(heartRate);
  Serial.print("\t");
  Serial.print("Distance: ");
  Serial.println(distance);
}

void initializeBLE() {
  Serial.println("Step 2: Initializing BLE");

  if (!BLE.begin()) {
    Serial.println("Step 2: BLE failed!");
    while (1);
  }

  Serial.println("Step 3: BLE Successful");
  BLE.scanForUuid("180D");
}

void discoverAndConnect() {
  BLEDevice peripheral = BLE.available();

  if (peripheral) {
    Serial.println("Step 4: Scanning Device");
    Serial.print("Peripheral Name: ");
    Serial.println(peripheral.localName());

    if (peripheral.localName() == "TICKR 0A5B") {
      Serial.println("Step 5: Device Found");
      Serial.println("Step 6: Connecting ...");
      BLE.stopScan();

      if (peripheral.connect()) {
        Serial.println("Step 7: Connected To Sensor");

        Serial.println("Step 8: Discovering attributes ...");
        if (peripheral.discoverAttributes()) {
          Serial.println("Step 9: Attributes Discovered Successfully");

          BLEService service180D = peripheral.service("180D");
          if (service180D) {
            BLECharacteristic characteristic2A37 = service180D.characteristic("2A37");
            if (characteristic2A37) {
              characteristic2A37.subscribe();
              Serial.println("Step 10: Connected to Data Stream of Sensor. Started Fetching Data ....");
              while (true) {
                peripheral.poll();
                if (characteristic2A37.valueUpdated()) {
                  printHeartRate(characteristic2A37.value(), characteristic2A37.valueLength());
                }
              }
            } else {
              Serial.println("Step 10: Characteristic 2A37 not found");
            }
          } else {
            Serial.println("Step 10: Service 180D not found");
          }
        } else {
          Serial.println("Step 9: Discovering attributes failed");
          peripheral.disconnect();
          return;
        }
      } else {
        Serial.println("Step 7: Connection Failed");
        return;
      }
    } else {
      Serial.println("Step 6: Sensor Not Found");
    }
  }
}

void printHeartRate(const unsigned char data[], int length) {
  for (int i = 0; i < length; i++) {
    if (i == 1) {
      unsigned char b = data[i];
      Serial.print("Heart Rate Value (BPM) = ");
      Serial.println(b);
    }
  }
}


ye hai