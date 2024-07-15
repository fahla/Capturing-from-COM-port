#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


def linear_interpolation(value, c_low, c_high, aqi_low, aqi_high):
    return round(((aqi_high - aqi_low) / (c_high - c_low)) * (value - c_low) + aqi_low)


# In[3]:


def calculate_aqi_pm25(pm25_lower, pm25_upper):
    aqi_values = []
    for pm25 in [pm25_lower, pm25_upper]:
        if pm25 <= 12.0:
            aqi_values.append(linear_interpolation(pm25, 0.0, 12.0, 0, 50))
        elif pm25 <= 35.4:
            aqi_values.append(linear_interpolation(pm25, 12.1, 35.4, 51, 100))
        elif pm25 <= 55.4:
            aqi_values.append(linear_interpolation(pm25, 35.5, 55.4, 101, 150))
        elif pm25 <= 150.4:
            aqi_values.append(linear_interpolation(pm25, 55.5, 150.4, 151, 200))
        elif pm25 <= 250.4:
            aqi_values.append(linear_interpolation(pm25, 150.5, 250.4, 201, 300))
        elif pm25 <= 350.4:
            aqi_values.append(linear_interpolation(pm25, 250.5, 350.4, 301, 400))
        elif pm25 <= 500.4:
            aqi_values.append(linear_interpolation(pm25, 350.5, 500.4, 401, 500))
        else:
            aqi_values.append(500)  # AQI value for concentrations above 500
    return min(aqi_values), max(aqi_values)


# In[4]:


def calculate_aqi_pm10(pm10_lower, pm10_upper):
    aqi_values = []
    for pm10 in [pm10_lower, pm10_upper]:
        if pm10 <= 54:
            aqi_values.append(linear_interpolation(pm10, 0, 54, 0, 50))
        elif pm10 <= 154:
            aqi_values.append(linear_interpolation(pm10, 55, 154, 51, 100))
        elif pm10 <= 254:
            aqi_values.append(linear_interpolation(pm10, 155, 254, 101, 150))
        elif pm10 <= 354:
            aqi_values.append(linear_interpolation(pm10, 255, 354, 151, 200))
        elif pm10 <= 424:
            aqi_values.append(linear_interpolation(pm10, 355, 424, 201, 300))
        elif pm10 <= 504:
            aqi_values.append(linear_interpolation(pm10, 425, 504, 301, 400))
        elif pm10 <= 604:
            aqi_values.append(linear_interpolation(pm10, 505, 604, 401, 500))
        else:
            aqi_values.append(500)  # AQI value for concentrations above 604
    return min(aqi_values), max(aqi_values)


# In[5]:


def apply_uncertainty(value, uncertainty=0.1):
    return value * (1 - uncertainty), value * (1 + uncertainty)


# In[6]:


def read_sensor_data(csv_file):
    data = pd.read_csv(csv_file, parse_dates=['Timestamp'])
    return data


# In[7]:


def calculate_aqi(data):
    data['pm25_lower'], data['pm25_upper'] = zip(*data['pm2.5'].apply(apply_uncertainty))
    data['pm10_lower'], data['pm10_upper'] = zip(*data['pm10.0'].apply(apply_uncertainty))
    
    data['pm2.5_aqi_lower'], data['pm2.5_aqi_upper'] = zip(*data.apply(lambda row: calculate_aqi_pm25(row['pm25_lower'], row['pm25_upper']), axis=1))
    data['pm10.0_aqi_lower'], data['pm10.0_aqi_upper'] = zip(*data.apply(lambda row: calculate_aqi_pm10(row['pm10_lower'], row['pm10_upper']), axis=1))
    
    data['pm2.5_aqi'] = data['pm2.5'].apply(lambda x: calculate_aqi_pm25(x, x)[0])
    data['pm10.0_aqi'] = data['pm10.0'].apply(lambda x: calculate_aqi_pm10(x, x)[0])
    
    data['overall_aqi_lower'] = data[['pm2.5_aqi_lower', 'pm10.0_aqi_lower']].max(axis=1)
    data['overall_aqi_upper'] = data[['pm2.5_aqi_upper', 'pm10.0_aqi_upper']].max(axis=1)
    data['overall_aqi'] = data[['pm2.5_aqi', 'pm10.0_aqi']].max(axis=1)
    return data


# In[8]:


def interval_analysis(data, interval='5min'):
    data.set_index('Timestamp', inplace=True)
    interval_data = data.resample(interval).agg({
        'pm2.5': ['min', 'max', 'mean'],
        'pm10.0': ['min', 'max', 'mean'],
        'pm2.5_aqi_lower': ['min', 'max', 'mean'],
        'pm2.5_aqi_upper': ['min', 'max', 'mean'],
        'pm10.0_aqi_lower': ['min', 'max', 'mean'],
        'pm10.0_aqi_upper': ['min', 'max', 'mean'],
        'overall_aqi_lower': ['min', 'max', 'mean'],
        'overall_aqi_upper': ['min', 'max', 'mean'],
        'overall_aqi': ['min', 'max', 'mean']
    })
    interval_data.columns = ['_'.join(col).strip() for col in interval_data.columns.values]
    interval_data.reset_index(inplace=True)
    return interval_data


# In[9]:


def aggregate_aqi_by_hour(interval_data):
    interval_data['date_hour'] = interval_data['Timestamp'].dt.floor('h')
    hourly_aqi = interval_data.groupby('date_hour').agg({
        'overall_aqi_mean': 'mean',
        'overall_aqi_lower_mean': 'mean',
        'overall_aqi_upper_mean': 'mean'
    }).reset_index()

    # Ensure there are no missing hourly values by reindexing and interpolating
    all_hours = pd.date_range(start=hourly_aqi['date_hour'].min(), 
                              end=hourly_aqi['date_hour'].max(), 
                              freq='h')
    hourly_aqi = hourly_aqi.set_index('date_hour').reindex(all_hours).reset_index()
    hourly_aqi.columns = ['date_hour', 'overall_aqi_mean', 'overall_aqi_lower_mean', 'overall_aqi_upper_mean']
    hourly_aqi['overall_aqi_mean'] = hourly_aqi['overall_aqi_mean'].interpolate()
    hourly_aqi['overall_aqi_lower_mean'] = hourly_aqi['overall_aqi_lower_mean'].interpolate()
    hourly_aqi['overall_aqi_upper_mean'] = hourly_aqi['overall_aqi_upper_mean'].interpolate()

    hourly_aqi['date'] = hourly_aqi['date_hour'].dt.date
    hourly_aqi['hour'] = hourly_aqi['date_hour'].dt.hour
    hourly_aqi = hourly_aqi[['date', 'hour', 'overall_aqi_mean', 'overall_aqi_lower_mean', 'overall_aqi_upper_mean']]
    # Round the overall AQI to the nearest integer
    hourly_aqi['overall_aqi_mean'] = hourly_aqi['overall_aqi_mean'].round().astype(int)
    hourly_aqi['overall_aqi_lower_mean'] = hourly_aqi['overall_aqi_lower_mean'].round().astype(int)
    hourly_aqi['overall_aqi_upper_mean'] = hourly_aqi['overall_aqi_upper_mean'].round().astype(int)
    return hourly_aqi


# In[11]:


def aqi_each_hour_main(csv_file, output_csv_file, output_csv_file_24h):
    data = read_sensor_data(csv_file)
    data = calculate_aqi(data)
    interval_data = interval_analysis(data)
    hourly_aqi = aggregate_aqi_by_hour(interval_data)

    # Save the hourly AQI analysis results to a CSV file
    hourly_aqi.to_csv(output_csv_file, index=False)

    # Read the hourly AQI data from the output file
    hourly_aqi = pd.read_csv(output_csv_file, parse_dates=[['date', 'hour']])

    # Combine 'date' and 'hour' columns to form 'Timestamp'
    hourly_aqi['Timestamp'] = pd.to_datetime(hourly_aqi['date_hour'])

    # Extract the latest 24 hours of data
    latest_24h_start = hourly_aqi['Timestamp'].max() - pd.Timedelta(hours=23)
    latest_24h = hourly_aqi[hourly_aqi['Timestamp'] >= latest_24h_start]

    # Interpolate to fill any missing values
    latest_24h.set_index('Timestamp', inplace=True)
    latest_24h = latest_24h.resample('H').mean().interpolate()

    # Round values to 2 decimal places
    latest_24h['AQI_PM2.5_24h'] = latest_24h['overall_aqi_mean'].round(2)
    latest_24h['AQI_PM10_24h'] = latest_24h['overall_aqi_mean'].round(2)

    # Reset index to get 'Timestamp' back as a column
    latest_24h.reset_index(inplace=True)

    # Select and rename columns
    latest_24h = latest_24h[['Timestamp', 'AQI_PM2.5_24h', 'AQI_PM10_24h']]

    # Save the latest 24 hours of AQI data to a separate CSV file
    latest_24h.to_csv(output_csv_file_24h, index=False)

# Example usage:
# aqi_each_hour_main("sensor_data.csv", "AQIAllHours.csv", "AQILast24Hours.csv")


    
# print("Hourly AQI analysis completed. Results saved to", output_csv_file)
# csv_file = 'sensor_data.csv'  # Replace with your actual file path
# aqi_each_hour_main(csv_file, "output_csv_file_all")

# In[12]:


# Example usage



# In[ ]:







