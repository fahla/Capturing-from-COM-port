import pandas as pd
from datetime import timedelta

def calculate_aqi_pm25(pm25):
    if pm25 <= 12.0:
        return linear_interpolation(pm25, 0.0, 12.0, 0, 50)
    elif pm25 <= 35.4:
        return linear_interpolation(pm25, 12.1, 35.4, 51, 100)
    elif pm25 <= 55.4:
        return linear_interpolation(pm25, 35.5, 55.4, 101, 150)
    elif pm25 <= 150.4:
        return linear_interpolation(pm25, 55.5, 150.4, 151, 200)
    elif pm25 <= 250.4:
        return linear_interpolation(pm25, 150.5, 250.4, 201, 300)
    elif pm25 <= 350.4:
        return linear_interpolation(pm25, 250.5, 350.4, 301, 400)
    elif pm25 <= 500.4:
        return linear_interpolation(pm25, 350.5, 500.4, 401, 500)
    else:
        return 500  # AQI value for concentrations above 500

def calculate_aqi_pm10(pm10):
    if pm10 <= 54:
        return linear_interpolation(pm10, 0, 54, 0, 50)
    elif pm10 <= 154:
        return linear_interpolation(pm10, 55, 154, 51, 100)
    elif pm10 <= 254:
        return linear_interpolation(pm10, 155, 254, 101, 150)
    elif pm10 <= 354:
        return linear_interpolation(pm10, 255, 354, 151, 200)
    elif pm10 <= 424:
        return linear_interpolation(pm10, 355, 424, 201, 300)
    elif pm10 <= 504:
        return linear_interpolation(pm10, 425, 504, 301, 400)
    elif pm10 <= 604:
        return linear_interpolation(pm10, 505, 604, 401, 500)
    else:
        return 500  # AQI value for concentrations above 604

def linear_interpolation(value, c_low, c_high, aqi_low, aqi_high):
    return ((aqi_high - aqi_low) / (c_high - c_low)) * (value - c_low) + aqi_low

def read_sensor_data(csv_file):
    data = pd.read_csv(csv_file, parse_dates=['Timestamp'])
    return data

def calculate_aqi(data):
    data['pm2.5_aqi'] = data['pm2.5'].apply(lambda x: round(calculate_aqi_pm25(x), 2))
    data['pm10.0_aqi'] = data['pm10.0'].apply(lambda x: round(calculate_aqi_pm10(x), 2))
    data['overall_aqi'] = data[['pm2.5_aqi', 'pm10.0_aqi']].max(axis=1).round(2)
    return data

def peak_hour_analysis(data):
    data['hour'] = data['Timestamp'].dt.hour
    peak_hours = data.groupby('hour').agg({
        'pm2.5_aqi': lambda x: round(x.mean(), 2),
        'pm10.0_aqi': lambda x: round(x.mean(), 2),
        'overall_aqi': lambda x: round(x.mean(), 2)
    }).reset_index()
    peak_hours = peak_hours.sort_values(by='overall_aqi', ascending=False)
    return peak_hours


def find_peak_hours(peak_hours, top_n=3):
    return peak_hours.head(top_n)

def peak_main(csv_file, output_csv_file, start_date, start_hour, end_date, end_hour):
    # Read the sensor data from the CSV file
    data = read_sensor_data(csv_file)
    
    # Filter the data based on the provided date and hour range
    start_datetime = pd.to_datetime(f"{start_date} {start_hour}")
    end_datetime = pd.to_datetime(f"{end_date} {end_hour}")
    data = data[(data['Timestamp'] >= start_datetime) & (data['Timestamp'] <= end_datetime)]
    
    # Calculate the AQI for the filtered data
    data = calculate_aqi(data)
    
    # Perform peak hour analysis
    peak_hours = peak_hour_analysis(data)
    top_peak_hours = find_peak_hours(peak_hours)

    # Save the peak hour analysis results to a CSV file
    top_peak_hours.to_csv(output_csv_file, index=False)

# Example usage (if needed for standalone testing)
# csv_file = '/path/to/sensor_data.csv'
# output_csv_file = '/path/to/peak_hour_analysis.csv'
# peak_main(csv_file, output_csv_file, '2024-07-01', '00:00', '2024-07-02', '23:59')
