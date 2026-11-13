#include <ArduinoBLE.h>

BLEDevice peripheral;
BLECharacteristic characteristic2A37;

void initializeBLE() {
  if (!BLE.begin()) {
    Serial.println("Step 2: BLE failed!");
    while (1);
  }
  Serial.println("Step 3: BLE Successful");
  BLE.scanForUuid("180D");
}

void setup() {
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Step 1: Starting Service");
  initializeBLE();
}

void loop() {
  BLE.poll();  // Poll for BLE events and communication updates.
}

void printData(const unsigned char data[], int length) {
  if (length >= 2) {
    unsigned char heartRate = data[1];
    Serial.print("Heart Rate Value (BPM) = ");
    Serial.println(heartRate);
  }
}

void discoverAndConnect() {
  peripheral = BLE.available();

  if (peripheral && peripheral.localName() == "TICKR 0A5B") {
    BLE.stopScan();
    if (peripheral.connect()) {
      Serial.println("Step 7: Connected To Sensor");

      if (peripheral.discoverAttributes()) {
        Serial.println("Step 9: Attributes Discovered Successfully");

        BLEService service180D = peripheral.service("180D");
        if (service180D) {
          characteristic2A37 = service180D.characteristic("2A37");
          if (characteristic2A37) {
            characteristic2A37.subscribe();
            Serial.println("Step 10: Connected to Data Stream of Sensor. Started Fetching Data ....");
          } else {
            Serial.println("Step 10: Characteristic 2A37 not found");
          }
        } else {
          Serial.println("Step 10: Service 180D not found");
        }
      } else {
        Serial.println("Step 9: Discovering attributes failed");
        peripheral.disconnect();
      }
    } else {
      Serial.println("Step 7: Connection Failed");
    }
  }
}

void loop() {
  discoverAndConnect();
  if (characteristic2A37 && characteristic2A37.valueUpdated()) {
    printData(characteristic2A37.value(), characteristic2A37.valueLength());
  }
}
