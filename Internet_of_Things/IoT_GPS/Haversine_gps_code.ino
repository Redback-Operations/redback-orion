#include <Arduino_LSM6DS3.h>
#include <Wire.h>
#include <TinyGPS++.h>
#include <SoftwareSerial.h>

#define GPS_TX_PIN 2 // GPS TX pin connected to Arduino RX pin
#define GPS_RX_PIN 3 // GPS RX pin connected to Arduino TX pin

SoftwareSerial gpsSerial(GPS_TX_PIN, GPS_RX_PIN);
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

void setup() {
  Serial.begin(9600);
  gpsSerial.begin(9600);
}

void loop() {
  while (gpsSerial.available() > 0) {
    if (gps.encode(gpsSerial.read())) {
      if (gps.location.isValid()) {
        // Read GPS coordinates
        double currentLat = gps.location.lat();
        double currentLon = gps.location.lng();
        
        static double previousLat = 0.0;
        static double previousLon = 0.0;
        static unsigned long previousTime = 0;
        
        unsigned long currentTime = millis();
        unsigned long elapsedTime = currentTime - previousTime;
        
        // Calculate distance every 5 seconds
        if (elapsedTime >= 5000) {
          // Calculate distance between previous and current coordinates
          double distance = haversine(previousLat, previousLon, currentLat, currentLon);
          
          Serial.print("Distance covered in the last 5 seconds (meters): ");
          Serial.println(distance);
          
          // Update previous coordinates and time
          previousLat = currentLat;
          previousLon = currentLon;
          previousTime = currentTime;
        }
      }
    }
  }
}
