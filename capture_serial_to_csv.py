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
                
                # parsing logic 
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
                        temperature = int(line.split('Received temperature: ')[1].split(' °C')[0])
                    except (ValueError, IndexError):
                        print("Error parsing temperature value")
                        continue
                elif line.startswith('Received humidity:'):
                    try:
                        humidity = int(line.split('Received humidity: ')[1].split(' percent RH')[0])
                    except (ValueError, IndexError):
                        print("Error parsing humidity value")
                        continue
                elif line.startswith('pm1.0:'):
                    try:
                        pm1_0 = float(line.split('pm1.0: ')[1])
                    except (ValueError, IndexError):
                        print("Error parsing humidity value")
                        continue
                elif line.startswith('pm2.5:'):
                    try:
                        pm2_5 = float(line.split('pm2.5: ')[1])
                    except (ValueError, IndexError):
                        print("Error parsing humidity value")
                        continue
                elif line.startswith('pm4.0:'):
                    try:
                        pm4_0 = float(line.split('pm4.0: ')[1])
                    except (ValueError, IndexError):
                        print("Error parsing humidity value")
                        continue
                elif line.startswith('pm10.0:'):
                    try:
                        pm10_0 = float(line.split('pm10.0: ')[1])
                    except (ValueError, IndexError):
                        print("Error parsing humidity value")
                        continue
                elif line.startswith('nc0.5:'):
                    try:
                        nc0_5 = float(line.split('nc0.5: ')[1])
                    except (ValueError, IndexError):
                        print("Error parsing humidity value")
                        continue
                elif line.startswith('nc1.0:'):
                    try:
                        nc1_0 = float(line.split('nc1.0: ')[1])
                    except (ValueError, IndexError):
                        print("Error parsing humidity value")
                        continue
                elif line.startswith('nc2.5:'):
                    try:
                        nc2_5 = float(line.split('nc2.5: ')[1])
                    except (ValueError, IndexError):
                        print("Error parsing humidity value")
                        continue
                elif line.startswith('nc10.0:'):
                    try:
                        nc10_0 = float(line.split('nc10.0: ')[1])
                    except (ValueError, IndexError):
                        print("Error parsing humidity value")
                        continue
                elif line.startswith('typical size:'):
                    try:
                        typical_size = float(line.split('typical size: ')[1])
                    except (ValueError, IndexError):
                        print("Error parsing humidity value")
                        continue

                
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
