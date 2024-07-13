import pandas as pd
from prophet import Prophet
import params as pr

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

def calculate_aqi_pm10(pm10):
    if 0.0 <= pm10 <= 54.0:
        aqi = (50 / 54.0) * pm10
    elif 55.0 <= pm10 <= 154.0:
        aqi = ((100 - 51) / (154 - 55)) * (pm10 - 55) + 51
    elif 155.0 <= pm10 <= 254.0:
        aqi = ((150 - 101) / (254 - 155)) * (pm10 - 155) + 101
    elif 255.0 <= pm10 <= 354.0:
        aqi = ((200 - 151) / (354 - 255)) * (pm10 - 255) + 151
    elif 355.0 <= pm10 <= 424.0:
        aqi = ((300 - 201) / (424 - 355)) * (pm10 - 355) + 201
    elif 425.0 <= pm10 <= 504.0:
        aqi = ((400 - 301) / (504 - 425)) * (pm10 - 425) + 301
    elif 505.0 <= pm10 <= 604.0:
        aqi = ((500 - 401) / (604 - 505)) * (pm10 - 505) + 401
    else:
        aqi = 500  # Any value beyond the last breakpoint is considered hazardous
    return round(aqi)


def main_function(input_file, output_file):
    data = pd.read_csv(input_file)
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    # data = data.interpolate()

    data['AQI_pm2.5'] = data['pm2.5'].apply(calculate_aqi_pm25)
    data['AQI_pm10'] = data['pm10.0'].apply(calculate_aqi_pm10)
    
    data['AQI'] = data[['AQI_pm2.5', 'AQI_pm10']].max(axis=1)
    # Resample to hourly frequency and calculate mean AQI
    data = data.set_index('Timestamp')
    hourly_data = data['AQI'].resample('H').mean().reset_index()
    
    # Prepare the data for Prophet
    df_prophet = hourly_data.rename(columns={'Timestamp': 'ds', 'AQI': 'y'})

    # Initialize and fit the model
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=True)
    model.fit(df_prophet)

    # Make future predictions
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    
    # New forecast logic
    forecast['yhat']=forecast['yhat'].apply(lambda x:max(x,0))


    # Extract and inspect predicted AQI values
    predicted_aqi = forecast[['ds', 'yhat']]
    predicted_aqi['hour'] = predicted_aqi['ds'].dt.hour

    # Group by the hour and calculate the mean predicted AQI
    predicted_hourly_aqi = predicted_aqi.groupby('hour')['yhat'].mean().round().reset_index()
    predicted_hourly_aqi.columns = ['hour', 'predicted_AQI']

    
    # Identify the hour with the highest AQI value
    # worst_hour = predicted_hourly_aqi.idxmax()
    # worst_aqi = predicted_hourly_aqi.max()
    
    # final_output = pd.DataFrame({
    #     'AQI': [worst_aqi],
    #     'time': [worst_hour]
    # })
    
    
    predicted_hourly_aqi.to_csv(output_file, index=False)
    

main_function(pr.CSV_FILE ,pr.PRED_FILE)