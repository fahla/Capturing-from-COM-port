import pandas as pd
from sklearn.preprocessing import StandardScaler
from prophet import Prophet

def main_function(input_file, output_file):
    data = pd.read_csv(input_file)
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    data = data.interpolate()

    # Calculate AQI from PM2.5
    def calculate_aqi_pm25(pm25):
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

    data['AQI'] = data['pm2.5'].apply(calculate_aqi_pm25)
  
    # Prepare the data for Prophet
    df_prophet = data[['Timestamp', 'AQI']].rename(columns={'Timestamp': 'ds', 'AQI': 'y'})

    # Initialize and fit the model
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=True)
    model.fit(df_prophet)

    # Make future predictions
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)

    # Extract and inspect predicted AQI values
    predicted_aqi = forecast[['ds', 'yhat']]
    predicted_aqi['hour'] = predicted_aqi['ds'].dt.hour

    # Group by the hour and calculate the mean predicted AQI
    predicted_hourly_aqi = predicted_aqi.groupby('hour')['yhat'].mean()
    
    # Generate textual summary
    summary = predicted_hourly_aqi.to_dict()
    print("Predicted AQI by Hour of the Day:")
    
    # Identify the hour with the highest AQI value
    worst_hour = predicted_hourly_aqi.idxmax()
    worst_aqi = predicted_hourly_aqi.max()    
    final_output = pd.DataFrame({
    'AQI': [worst_aqi],
    'time': [worst_hour] })
    final_output.to_csv(output_file)