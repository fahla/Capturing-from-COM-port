import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

# Function to calculate AQI based on pm2.5
def calculate_aqi(pm25):
    if 0.0 <= pm25 <= 12.0:
        aqi = (50 / 12.0) * pm25
    elif 12.1 <= pm25 <= 35.4:
        aqi = ((100 - 51) / (35.4 - 12.1)) * (pm25 - 12.1) + 51
    elif 35.5 <= pm25 <= 55.4:
        aqi = ((150 - 101) / (55.4 - 35.5)) * (pm25 - 35.5) + 101
    elif 55.5 <= pm25 <= 150.4:
        aqi = ((200 - 151) / (150.4 - 55.5)) * (pm25 - 55.5) + 151
    elif 150.5 <= pm25 <= 250.4:
        aqi = ((300 - 201) / (250.4 - 150.5)) * (pm25 - 150.5) + 201
    elif 250.5 <= pm25 <= 350.4:
        aqi = ((400 - 301) / (350.4 - 250.5)) * (pm25 - 250.5) + 301
    elif 350.5 <= pm25 <= 500.4:
        aqi = ((500 - 401) / (500.4 - 350.5)) * (pm25 - 350.5) + 401
    else:
        aqi = 500
    return round(aqi)

# Load the data
file_path = 'sensor_data.csv'
data = pd.read_csv(file_path)

# Convert Timestamp to datetime
data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# Calculate AQI
data['AQI'] = data['pm2.5'].apply(calculate_aqi)

# Set the Timestamp as the index
data.set_index('Timestamp', inplace=True)

# Resample data to hourly average
hourly_data = data['AQI'].resample('H').mean()

# Calculate the lowest and highest AQI from the source data
lowest_aqi = data['AQI'].min()
lowest_aqi_time = data['AQI'].idxmin()
highest_aqi = data['AQI'].max()
highest_aqi_time = data['AQI'].idxmax()

# Split the data into training and testing sets
train_data = hourly_data[:-24]
test_data = hourly_data[-24:]

# Build and fit the ARIMA model
model = ARIMA(train_data, order=(5, 1, 0))
model_fit = model.fit()

# Forecast the next 24 hours
forecast = model_fit.forecast(steps=24)
forecast_index = pd.date_range(start=hourly_data.index[-1] + pd.Timedelta(hours=1), periods=24, freq='H')

# Create a DataFrame for the predictions
forecast_df = pd.DataFrame({'Timestamp': forecast_index, 'Predicted AQI': forecast})

# Format the Timestamp for better readability
forecast_df['Hour'] = forecast_df['Timestamp'].dt.strftime('%I:%M %p')
forecast_df = forecast_df[['Hour', 'Predicted AQI']]

# Print the lowest and highest AQI from the source data
print(f"Lowest AQI: {lowest_aqi} at {lowest_aqi_time}")
print(f"Highest AQI: {highest_aqi} at {highest_aqi_time}")

# Print the forecasted AQI values
print(forecast_df.to_string(index=False))

# Save the forecast to a CSV file
forecast_df.to_csv('forecasted_aqi.csv', index=False)
