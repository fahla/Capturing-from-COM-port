# Parameters for capturing data
SERIAL_PORT = 'COM12'  # Adjust as necessary
BAUD_RATE = 115200
CSV_FILE = r'sensor_data.csv' 

# Parameters for peak hour analysis
START_DATE = '2024-07-05'
START_HOUR = '00:00'
END_DATE = '2024-07-25'
END_HOUR = '23:59'
PEAK_HOUR_FILE = 'peak_hour_data_new.csv'
PRED_FILE = 'pred_file_latest.csv'
AQI_DATA_LAST24_HOURS = 'aqi_data_last_24hrs.csv'
AQI_DATA_ALL = 'AQIAllHours.csv'

# FTP details
FTP_DETAILS = {
    'server': 'ftp.gb.stackcp.com',
    'username': 'ssns@cillyfox.com',
    'password': '#SSNS9167',
    'directory': ''
}
