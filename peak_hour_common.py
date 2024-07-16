import pandas as pd

def linear_interpolation(value, c_low, c_high, aqi_low, aqi_high):
    return ((aqi_high - aqi_low) / (c_high - c_low)) * (value - c_low) + aqi_low

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

def read_sensor_data(csv_file):
    data = pd.read_csv(csv_file, parse_dates=['Timestamp'])
    return data

def calculate_aqi(data):
    data['AQI_PM2.5'] = data['pm2.5'].apply(lambda x: round(calculate_aqi_pm25(x), 2))
    data['AQI_PM10'] = data['pm10.0'].apply(lambda x: round(calculate_aqi_pm10(x), 2))
    data['AQI'] = data[['AQI_PM2.5', 'AQI_PM10']].max(axis=1).round(2)
    return data

def peak_hour_analysis(data):
    data['hour'] = data['Timestamp'].dt.floor('h')
    hourly_data = data.groupby('hour').mean().reset_index()

    # Round off all values to 2 decimal places
    hourly_data = hourly_data.round(2)

    max_aqi_pm25 = hourly_data['AQI_PM2.5'].max()
    max_aqi_pm10 = hourly_data['AQI_PM10'].max()
    max_temp = hourly_data['Temperature (C)'].max()
    max_co2 = hourly_data['CO2 (ppm)'].max()

    hourly_data['Peak_Hour_AQI_PM2.5'] = (hourly_data['AQI_PM2.5'] == max_aqi_pm25).astype(int)
    hourly_data['Peak_Hour_AQI_PM10'] = (hourly_data['AQI_PM10'] == max_aqi_pm10).astype(int)
    hourly_data['Peak_Hour_Temperature'] = (hourly_data['Temperature (C)'] == max_temp).astype(int)
    hourly_data['Peak_Hour_CO2'] = (hourly_data['CO2 (ppm)'] == max_co2).astype(int)

    # Rename 'hour' back to 'Timestamp' for output consistency
    hourly_data.rename(columns={'hour': 'Timestamp'}, inplace=True)

    return hourly_data[['Timestamp', 'AQI_PM2.5', 'AQI_PM10', 'Temperature (C)', 'CO2 (ppm)',
                        'Peak_Hour_AQI_PM2.5', 'Peak_Hour_AQI_PM10', 'Peak_Hour_Temperature', 'Peak_Hour_CO2']]

def interpolate_missing_hours(df):
    df.set_index('Timestamp', inplace=True)
    df = df.resample('H').asfreq()
    df = df.interpolate(method='linear')
    df = df.reset_index()
    df = df.round(2)
    
    # Ensure peak hour indicators are correct after interpolation
    max_aqi_pm25 = df['AQI_PM2.5'].max()
    max_aqi_pm10 = df['AQI_PM10'].max()
    max_temp = df['Temperature (C)'].max()
    max_co2 = df['CO2 (ppm)'].max()

    df['Peak_Hour_AQI_PM2.5'] = (df['AQI_PM2.5'] == max_aqi_pm25).astype(int)
    df['Peak_Hour_AQI_PM10'] = (df['AQI_PM10'] == max_aqi_pm10).astype(int)
    df['Peak_Hour_Temperature'] = (df['Temperature (C)'] == max_temp).astype(int)
    df['Peak_Hour_CO2'] = (df['CO2 (ppm)'] == max_co2).astype(int)

    return df

def analyze_peak_hours(input_file, output_file, start_date, start_hour, end_date, end_hour):
    """Perform peak hour analysis."""
    try:
        data = read_sensor_data(input_file)

        # Filter the data based on the provided date and hour range
        start_datetime = pd.to_datetime(f"{start_date} {start_hour}")
        end_datetime = pd.to_datetime(f"{end_date} {end_hour}")
        data = data[(data['Timestamp'] >= start_datetime) & (data['Timestamp'] <= end_datetime)]

        # Calculate AQI for the filtered data
        data = calculate_aqi(data)

        # Perform peak hour analysis
        peak_hour_data = peak_hour_analysis(data)

        # Drop duplicate 'Timestamp' column if exists
        if 'Timestamp' in peak_hour_data.columns:
            peak_hour_data = peak_hour_data.loc[:, ~peak_hour_data.columns.duplicated()]

        # Interpolate missing hours
        peak_hour_data = interpolate_missing_hours(peak_hour_data)

        # Save the peak hour analysis results to a CSV file
        peak_hour_data.to_csv(output_file, index=False)
    except Exception as e:
        print(f"Error analyzing peak hours: {e}")

# Example usage (if needed for standalone testing)
if __name__ == "__main__":
    input_file = 'sensor_data.csv'  # Update this path as needed
    output_file = 'peak_hour_data_new.csv'  # Update this path as needed
    start_date = '2024-07-01'
    start_hour = '00:00'
    end_date = '2024-07-02'
    end_hour = '23:59'
    analyze_peak_hours(input_file, output_file, start_date, start_hour, end_date, end_hour)
