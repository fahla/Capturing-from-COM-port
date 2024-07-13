import capture_serial_to_csv as capture
import testread2 as upload
import peak_hour_common as peak
import time
import os
import params
import aqi_each_hour as aqi_hour
import serial
import Prediction_Model as pred

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
       peak.peak_main(input_file, output_file, start_date, start_hour, end_date, end_hour)

    except Exception as e:
        print(f"Error analyzing peak hours: {e}")

#SAMYAK
def generate_hourly_data(input_file, output_file):
    """Generate hourly data for the next 24 hours."""
    # Placeholder for generating hourly data
    pass

def generate_prediction_data(input_file, output_file):
    """Prophet Model"""
    try:
        pred.main_function(input_file,output_file)
        
    except Exception as e:
        print(f"Error in Model Prediction")
        
#anyone with more than 2 braincells can pick
def generate_daily_avg_data(input_file, output_file):
    """Generate a CSV file for daily average data."""
    # Placeholder for generating daily average data
    pass

#riya
def conduct_peak_hour_temp_co2(input_file, output_file):
    """Conduct peak hour analysis for temperature and CO2."""
    # Placeholder for peak hour analysis for temperature and CO2
    pass

#anvita
def generate_aqi_last_24_hours(input_file, output_file):
    """Generate a CSV for AQI data over the last 24 hours."""
    try:
        aqi_hour.aqi_each_hour_main(input_file, output_file)
    except Exception as e:
        print(f"Error in finding AQI for past hours: {e}")
        

def main():
    while True:
        try:
            #Capture the data 
            capture_data(params.SERIAL_PORT, params.BAUD_RATE, params.CSV_FILE)
            
            #Upload the sensor data CSV file
            #upload_data(params.CSV_FILE, **params.FTP_DETAILS)

            # Perform and upload peak hour analysis
            analyze_peak_hours(
                input_file=params.CSV_FILE,
                output_file=params.PEAK_HOUR_FILE,
                start_date=params.START_DATE,
                start_hour=params.START_HOUR,
                end_date=params.END_DATE,
                end_hour=params.END_HOUR
            )
            #upload_data(params.PEAK_HOUR_FILE, **params.FTP_DETAILS)
            #generate_prediction_data(params.PEAK_HOUR_FILE,params.PRED_FILE)
            # Generate and upload hourly data for the next 24 hours
            #generate_hourly_data(params.CSV_FILE, 'hourly_data_last_next_24_hours.csv')
            #upload_data('hourly_data_last_next_24_hours.csv', **params.FTP_DETAILS)

            # Generate and upload daily average data
            #generate_daily_avg_data(params.CSV_FILE, 'daily_avg_data.csv')
            #upload_data('daily_avg_data.csv', **params.FTP_DETAILS)

            # Conduct and upload peak hour analysis for temperature and CO2
            # conduct_peak_hour_temp_co2(params.CSV_FILE, 'peak_hour_temp_co2.csv')
            #upload_data('peak_hour_temp_co2.csv', **params.FTP_DETAILS)

            # Generate and upload AQI data for the last 24 hours
            #generate_aqi_last_24_hours(params.CSV_FILE, 'aqi_data_last_24_hours.csv')
            #upload_data('aqi_data_last_24_hours.csv', **params.FTP_DETAILS)
            
            time.sleep(10)  # Wait for 120 secs before next upload
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(60)  # Wait for 1 minute before retrying

if __name__ == "__main__":
    main()
