#include <TinyGPS++.h>
#include <Arduino_LSM6DS3.h>
#include <Wire.h>

// Define an instance of the TinyGPS++ object
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
  Serial.begin(9600); // Initialize hardware serial for communication with the serial monitor
  Serial1.begin(9600); // Initialize hardware serial for communication with the GPS module
}

void loop() {
  while (Serial1.available() > 0) {
    if (gps.encode(Serial1.read())) {
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
          
          // Print the two sets of coordinates and the distance
          Serial.print("Previous Latitude: ");
          Serial.print(previousLat, 10);
          Serial.print(", Previous Longitude: ");
          Serial.println(previousLon, 10);
          
          Serial.print("Current Latitude: ");
          Serial.print(currentLat, 10);
          Serial.print(", Current Longitude: ");
          Serial.println(currentLon, 10);
          
          Serial.print("Distance: ");
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
