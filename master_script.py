import capture_serial_to_csv as capture
import testread2 as upload
import peak_hour_analysis as peak
import time
import os

def capture_data(serial_port, baud_rate, csv_file):
    """Start capturing data from the serial port."""
    capture.start_capture(serial_port, baud_rate, csv_file)

def upload_data(csv_file, server, username, password, directory):
    """Upload the CSV file to the FTP server."""
    upload.upload_file_to_ftp(
        filename=csv_file, 
        server=server, 
        username=username, 
        password=password, 
        directory=directory
    )

def analyze_peak_hours(input_file, output_file, start_date, start_hour, end_date, end_hour):
    """Perform peak hour analysis."""
    peak.peak_main(input_file, output_file, start_date, start_hour, end_date, end_hour)

def main():
    serial_port = '/dev/tty.usbmodem0010502577971'  # Adjust as necessary
    baud_rate = 115200
    csv_file = 'sensor_data.csv'
    
    # Start capturing serial data in a separate thread or process if needed
    #capture_data(serial_port, baud_rate, csv_file)
    
    # Periodically upload the file to the server
    i=1
    while i<2:
        #upload_data(csv_file=csv_file, server='ftp.gb.stackcp.com', username='ssns@cillyfox.com', password='#SSNS9167',  directory='' )
        
        # Perform peak hour analysis
        analyze_peak_hours(
            input_file=csv_file,
            output_file='peak_hour_analysis.csv',
            start_date='2024-07-03',
            start_hour='00:00',
            end_date='2024-07-05',
            end_hour='23:59'
        )
        i=i+1 
      #  time.sleep(3600)  # Wait for 1 hour before uploading again

if __name__ == "__main__":
    main()
