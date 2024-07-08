# In[10]:


import pandas as pd
import numpy as np


# In[11]:


def linear_interpolation(value, c_low, c_high, aqi_low, aqi_high):
    return round(((aqi_high - aqi_low) / (c_high - c_low)) * (value - c_low) + aqi_low)


# In[12]:


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


# In[13]:


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


# In[14]:


def read_sensor_data(csv_file):
    data = pd.read_csv(csv_file, parse_dates=['Timestamp'])
    return data


# In[15]:


def calculate_aqi(data):
    data['pm2.5_aqi'] = data['pm2.5'].apply(calculate_aqi_pm25)
    data['pm10.0_aqi'] = data['pm10.0'].apply(calculate_aqi_pm10)
    data['overall_aqi'] = data[['pm2.5_aqi', 'pm10.0_aqi']].max(axis=1)
    return data


# In[16]:


def interval_analysis(data, interval='5min'):
    data.set_index('Timestamp', inplace=True)
    interval_data = data.resample(interval).agg({
        'pm2.5': ['min', 'max', 'mean'],
        'pm10.0': ['min', 'max', 'mean'],
        'pm2.5_aqi': ['min', 'max', 'mean'],
        'pm10.0_aqi': ['min', 'max', 'mean'],
        'overall_aqi': ['min', 'max', 'mean']
    })
    interval_data.columns = ['_'.join(col).strip() for col in interval_data.columns.values]
    interval_data.reset_index(inplace=True)
    return interval_data


# In[20]:


def aggregate_aqi_by_hour(interval_data):
    interval_data['date_hour'] = interval_data['Timestamp'].dt.floor('h')
    hourly_aqi = interval_data.groupby('date_hour')['overall_aqi_mean'].mean().reset_index()

    # Ensure there are no missing hourly values by reindexing and interpolating
    all_hours = pd.date_range(start=hourly_aqi['date_hour'].min(), 
                              end=hourly_aqi['date_hour'].max(), 
                              freq='h')
    hourly_aqi = hourly_aqi.set_index('date_hour').reindex(all_hours).reset_index()
    hourly_aqi.columns = ['date_hour', 'overall_aqi_mean']
    hourly_aqi['overall_aqi_mean'] = hourly_aqi['overall_aqi_mean'].interpolate()

    hourly_aqi['date'] = hourly_aqi['date_hour'].dt.date
    hourly_aqi['hour'] = hourly_aqi['date_hour'].dt.hour
    hourly_aqi = hourly_aqi[['date', 'hour', 'overall_aqi_mean']]
    # Round the overall AQI to the nearest integer
    hourly_aqi['overall_aqi_mean'] = hourly_aqi['overall_aqi_mean'].round().astype(int)
    return hourly_aqi


# In[21]:


def aqi_each_hour_main(csv_file, output_csv_file):
    data = read_sensor_data(csv_file)
    data = calculate_aqi(data)
    interval_data = interval_analysis(data)
    hourly_aqi = aggregate_aqi_by_hour(interval_data)

    # Save the hourly AQI analysis results to a CSV file
    hourly_aqi.to_csv(output_csv_file, index=False)

    print("Hourly AQI analysis completed. Results saved to", output_csv_file)


# In[23]:


# Example usage
#csv_file = '/Users/hallo/Desktop/SSNS/project_data/sensor_data.csv'  # Replace with your actual file path
#output_csv_file = '/Users/hallo/Desktop/SSNS/project_data/aqi_hist.csv'  # Replace with your desired output file path

#aqi_each_hour_main(csv_file, output_csv_file)


