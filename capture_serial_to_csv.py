import serial
import csv
from datetime import datetime
import os

# Serial port settings
SERIAL_PORT = 'COM12'  # Adjust this to your serial port
BAUD_RATE = 115200

# CSV file settings
CSV_FILE = r"C:\nrf_connect_sdk\myprojects\sensor_data.csv"  # Adjust path as necessary
CSV_HEADER = ['Timestamp', 'eCO2 (ppm)', 'eTVOC (ppb)', 'CO2 (ppm)', 'Temperature (°C)', 'Humidity (%)']

def read_from_serial(port, baud_rate):
    """Reads data from the specified serial port."""
    ser = serial.Serial(port, baud_rate)
    ser.flushInput()
    return ser

def write_to_csv(file_name, data):
    """Writes data to a CSV file."""
    try:
        with open(file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
            print(f"Data written to CSV: {data}")  # Debugging print
    except IOError as e:
        print(f"Error writing to CSV file: {e}")

def main():
    ser = read_from_serial(SERIAL_PORT, BAUD_RATE)
    print(f"Listening on {SERIAL_PORT} at {BAUD_RATE} baud rate.")
    
    # Check if CSV file exists, create it if it doesn't
    if not os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(CSV_HEADER)
        except IOError as e:
            print(f"Error creating CSV file: {e}")
            return  # Exit function if file creation fails
    
    # Initialize variables for sensor values
    eCO2 = None
    eTVOC = None
    CO2 = None
    temperature = None
    humidity = None
    
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                print(f"Received: {line}")
                
                # Parse the line and unpack values
                if line.startswith('Received eCO2 value:'):
                    try:
                        eCO2 = int(line.split('Received eCO2 value: ')[1].split(' ppm')[0])
                    except (ValueError, IndexError):
                        print("Error parsing eCO2 value")
                        continue
                elif line.startswith('Received eTVOC value:'):
                    try:
                        eTVOC = int(line.split('Received eTVOC value: ')[1].split(' ppb')[0])
                    except (ValueError, IndexError):
                        print("Error parsing eTVOC value")
                        continue
                elif line.startswith('Received CO2 value:'):
                    try:
                        CO2 = int(line.split('Received CO2 value: ')[1].split(' ppm')[0])
                    except (ValueError, IndexError):
                        print("Error parsing CO2 value")
                        continue
                elif line.startswith('Received temperature:'):
                    try:
                        temperature = float(line.split('Received temperature: ')[1].split(' °C')[0])
                    except (ValueError, IndexError):
                        print("Error parsing temperature value")
                        continue
                elif line.startswith('Received humidity:'):
                    try:
                        humidity = float(line.split('Received humidity: ')[1].split(' percent RH')[0])
                    except (ValueError, IndexError):
                        print("Error parsing humidity value")
                        continue
                
                # Check if all values are received
                if all(v is not None for v in [eCO2, eTVOC, CO2, temperature, humidity]):
                    # Get current timestamp
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Write to CSV
                    data_row = [timestamp, eCO2, eTVOC, CO2, temperature, humidity]
                    write_to_csv(CSV_FILE, data_row)
                    
                    # Reset variables
                    eCO2 = None
                    eTVOC = None
                    CO2 = None
                    temperature = None
                    humidity = None
            
    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        ser.close()

if __name__ == '__main__':
    main()
