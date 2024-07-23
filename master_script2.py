import capture_serial_to_csv as capture
import testread2 as upload
import peak_hour_common as peak
import time
import os
import params
import aqi_each_hour as aqi_hour
import serial
#import Prediction_Model as pred
import random_forest as pred2

def read_from_serial(port, baud_rate):
    ser = serial.Serial(port, baud_rate)
    ser.flushInput()
    return ser

def capture_data(SERIAL_PORT, BAUD_RATE, CSV_FILE):
    """Start capturing data from the serial port."""
    ser = read_from_serial(SERIAL_PORT, BAUD_RATE)
    try:
        capture.start_capture(SERIAL_PORT,BAUD_RATE,CSV_FILE, ser)
    except Exception as e:
        print(f"Error capturing data: {e}")

def upload_data(file_name, server, username, password, directory):
    """Upload the CSV file to the FTP server."""
    try:
        upload.upload_file_to_ftp(
            filename=file_name, 
            server=server, 
            username=username, 
            password=password, 
            directory=directory
        )
    except Exception as e:
        print(f"Error uploading file {file_name}: {e}")

def analyze_peak_hours(input_file, output_file, start_date, start_hour, end_date, end_hour):
    """Perform peak hour analysis."""
    try:
        peak.analyze_peak_hours(input_file, output_file, start_date, start_hour, end_date, end_hour)

    except Exception as e:
        print(f"Error analyzing peak hours: {e}")

def generate_prediction_data_rf(input_file,output_file):
    """Random Forest"""
    try:
        pred2.forecast_aqi(input_file,output_file)
        
    except Exception as e:
        print(f"Error in Model Prediction")
        
def generate_daily_avg_data(input_file, output_file):
    """Generate a CSV file for daily average data."""
    # Placeholder for generating daily average data
    pass

def generate_aqi_data(input_file, output_file,output_file_24h):
    """Generate a CSV for AQI data over the last 24 hours."""
    try: 
        aqi_hour.aqi_each_hour_main(input_file, output_file,output_file_24h)
    except Exception as e:
        print(f"Error in finding AQI for past hours: {e}")
        

def main():
    initIteration=True
    while True:
        try:
            #Capture the data 
            #capture_data(params.SERIAL_PORT, params.BAUD_RATE, params.CSV_FILE)      
            #Upload the sensor data CSV file
            upload_data(params.CSV_FILE, **params.FTP_DETAILS)
            # Perform and upload peak hour analysis
            analyze_peak_hours(
                input_file=params.CSV_FILE,
                output_file=params.PEAK_HOUR_FILE,
                start_date=params.START_DATE,
                start_hour=params.START_HOUR,
                end_date=params.END_DATE,
                end_hour=params.END_HOUR
            )
            upload_data(params.PEAK_HOUR_FILE, **params.FTP_DETAILS)           
            generate_aqi_data(params.CSV_FILE ,params.AQI_DATA_ALL, params.AQI_DATA_LAST24_HOURS)
            upload_data(params.AQI_DATA_LAST24_HOURS, **params.FTP_DETAILS)  
            time.sleep(10)  # Wait for 120 secs before next upload
            if(initIteration):
                generate_prediction_data_rf(params.AQI_DATA_ALL,params.PRED_FILE)
                upload_data(params.PRED_FILE, **params.FTP_DETAILS)
            #  initIteration=False
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)  # Wait for 1 minute before retrying

def upload_files_fixed():
    initIteration=True
    #Upload the sensor data CSV file
   # upload_data(params.CSV_FILE, **params.FTP_DETAILS)
    # Perform and upload peak hour analysis
    analyze_peak_hours(
        input_file=params.CSV_FILE,
        output_file=params.PEAK_HOUR_FILE,
        start_date=params.START_DATE,
        start_hour=params.START_HOUR,
        end_date=params.END_DATE,
        end_hour=params.END_HOUR
    )
    upload_data(params.PEAK_HOUR_FILE, **params.FTP_DETAILS)           
    generate_aqi_data(params.CSV_FILE ,params.AQI_DATA_ALL, params.AQI_DATA_LAST24_HOURS)
    upload_data(params.AQI_DATA_LAST24_HOURS, **params.FTP_DETAILS)  
    #time.sleep(10)  # Wait for 120 secs before next upload
    if(initIteration):
        generate_prediction_data_rf(params.AQI_DATA_ALL,params.PRED_FILE)
        upload_data(params.PRED_FILE, **params.FTP_DETAILS)
        initIteration=False
    
if __name__ == "__main__":
    main()
