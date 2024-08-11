# Save this as collect_data.py

import serial
import time

# Setup your serial port and baud rate. Replace '/dev/tty.usbmodemXXXX' with your actual device port
serial_port = '/dev/tty.usbmodemXXXX'
baud_rate = 115200

try:
    ser = serial.Serial(serial_port, baud_rate)
    # Allow time for serial connection to initialize
    time.sleep(2)
    print("Connected to Arduino. Collecting data...")

    with open("output.csv", "w") as file:
        while True:
            data = ser.readline().decode().strip()  # read data from serial and decode it
            file.write(data + "\n")  # write data to CSV file
            print(data)  # print data to console

except serial.SerialException:
    print(f"Failed to connect on {serial_port}")
except KeyboardInterrupt:
    print("Interrupted by user, stopping data collection.")
finally:
    ser.close()  # Ensure serial connection is closed on exit
