#include <ArduinoBLE.h>
#include <TinyGPS++.h>

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
  double a = sin(dLat/2) * sin(dLat/2) + cos(toRadians(lat1)) * cos(toRadians(lat2)) * sin(dLon/2) * sin(dLon/2);
  double c = 2 * atan2(sqrt(a), sqrt(1-a));
  return EARTH_RADIUS * c;
}

// Function Declarations
void initializeBLE();
void discoverAndConnect();
void printData(const unsigned char data[], int length);

void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
  while (!Serial);
  Serial.println("Step 1: Starting Service");
  initializeBLE();
}

void loop() {
  discoverAndConnect();
  BLE.poll();  // Poll for BLE events and communication updates.
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
                  printData(characteristic2A37.value(), characteristic2A37.valueLength());
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

void printData(const unsigned char data[], int length) {
  static unsigned long previousUpdateTime = 0;
  static unsigned long previousHeartRateTime = 0;
  
  for (int i = 0; i < length; i++) {
    if (i == 1) {
      unsigned char b = data[i];
      // Serial.print("Heart Rate Value (BPM) = ");
      // Serial.println(b);
      
      unsigned long currentTime = millis();
      // Check if 5 seconds have passed since the last update
      if (currentTime - previousUpdateTime >= 5000) {
        previousUpdateTime = currentTime; // Update the previous update time
        
        // Read GPS coordinates
        while (Serial1.available() > 0) {
          if (gps.encode(Serial1.read())) {
            if (gps.location.isValid()) {
              // Read GPS coordinates
              double currentLat = gps.location.lat();
              double currentLon = gps.location.lng();
              static double previousLat = 0.0;
              static double previousLon = 0.0;

              // Calculate distance between previous and current coordinates
              double distance = haversine(previousLat, previousLon, currentLat, currentLon);
              // Print the distance if it's greater than 0
              if (distance > 0) {
                Serial.print("Distance: ");
                Serial.println(distance);
              }
              // Update previous coordinates
              previousLat = currentLat;
              previousLon = currentLon;
              break; // Exit the while loop after processing GPS data once
            }
          }
        }
      }
      
      // Check if 5 seconds have passed since the last heart rate update
      if (currentTime - previousHeartRateTime >= 5000) {
        previousHeartRateTime = currentTime; // Update the previous heart rate update time
        Serial.print("Heart Rate Value (BPM) = ");
        Serial.println(b);
      }
    }
  }
}
