import serial
import csv
from datetime import datetime
import os

CSV_HEADER = ['Timestamp', 'eCO2 (ppm)', 'eTVOC (ppb)', 'CO2 (ppm)', 'Temperature (C)', 'Humidity',
              'pm1.0', 'pm2.5', 'pm4.0', 'pm10.0', 'nc0.5', 'nc1.0', 'nc2.5', 'nc10.0', 'typical size']

def read_from_serial(port, baud_rate):
    ser = serial.Serial(port, baud_rate)
    ser.flushInput()
    return ser

def write_to_csv(file_name, data):
    try:
        with open(file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
            print(f"Data written to CSV: {data}")
    except IOError as e:
        print(f"Error writing to CSV file: {e}")

def start_capture(serial_port, baud_rate, csv_file):
    ser = read_from_serial(serial_port, baud_rate)
    print(f"Listening on {serial_port} at {baud_rate} baud rate.")
    
    if not os.path.exists(csv_file):
        try:
            with open(csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(CSV_HEADER)
        except IOError as e:
            print(f"Error creating CSV file: {e}")
            return
    
    eCO2, eTVOC, CO2, temperature, humidity, pm1_0, pm2_5, pm4_0, pm10_0, nc0_5, nc1_0, nc2_5, nc10_0, typical_size = [None]*15
    
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                print(f"Raw data: {line}")
                
                # Add parsing logic here
                
                if all(v is not None for v in [eCO2, eTVOC, CO2, temperature, humidity,pm1_0, pm2_5, pm4_0, pm10_0, nc0_5, nc1_0, nc2_5, nc10_0, typical_size]):
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    data_row = [timestamp, eCO2, eTVOC, CO2, temperature, humidity, 
                                pm1_0, pm2_5, pm4_0, pm10_0, nc0_5, nc1_0, nc2_5, nc10_0, typical_size]
                    write_to_csv(csv_file, data_row)
                    
                    eCO2, eTVOC, CO2, temperature, humidity, pm1_0, pm2_5, pm4_0, pm10_0, nc0_5, nc1_0, nc2_5, nc10_0, typical_size = [None]*15
    
    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        ser.close()
