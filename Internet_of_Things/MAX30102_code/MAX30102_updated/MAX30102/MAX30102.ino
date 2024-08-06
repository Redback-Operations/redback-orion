#include <ArduinoBLE.h>
#include "DFRobot_BloodOxygen_S.h"

#define I2C_ADDRESS 0x57
DFRobot_BloodOxygen_S_I2C MAX30102(&Wire, I2C_ADDRESS);

unsigned long previousMillis = 0;
const long interval = 2000;  // Interval at which to read sensor data

void setup() {
  Serial.begin(115200);
  while (!Serial);
  initializeBLE();
  initializeSensor();
}

void loop() {
  unsigned long currentMillis = millis();

  // Perform BLE discovery and connection checking
  discoverAndConnect();
  BLE.poll();  // Poll for BLE events and communication updates.

  // Read sensor data at specified intervals
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    readAndPrintSensorData();
  }
}

void initializeBLE() {
  if (!BLE.begin()) {
    Serial.println("BLE initialization failed!");
    while (1);
  }
  BLE.scanForUuid("180D");
}

void discoverAndConnect() {
  BLEDevice peripheral = BLE.available();
  if (peripheral) {
    if (peripheral.localName() == "TICKR 0A5B") {
      BLE.stopScan();
      if (peripheral.connect()) {
        BLEService service180D = peripheral.service("180D");
        if (service180D) {
          BLECharacteristic characteristic2A37 = service180D.characteristic("2A37");
          if (characteristic2A37) {
            characteristic2A37.subscribe();
            while (peripheral.connected()) {
              peripheral.poll();
              if (characteristic2A37.valueUpdated()) {
                printHeartRateData(characteristic2A37.value(), characteristic2A37.valueLength());
              }
            }
            peripheral.disconnect();
          }
        }
      }
    }
  }
}

void printHeartRateData(const unsigned char data[], int length) {
  for (int i = 0; i < length; i++) {
    Serial.print("Heart Rate Value (BPM) = ");
    Serial.println(data[i]);
  }
}

void initializeSensor() {
  while (!MAX30102.begin()) {
    Serial.println("Sensor initialization failed, retrying...");
    delay(1000);
  }
  Serial.println("Sensor initialized successfully.");
}

void readAndPrintSensorData() {
  Serial.print("SPO2 is : ");
  Serial.print(MAX30102._sHeartbeatSPO2.SPO2);
  Serial.println("%");

}
