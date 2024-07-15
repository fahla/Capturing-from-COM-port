import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Load the data
file_path = 'sensor_data_aqi.csv'
data = pd.read_csv(file_path)

# Convert Timestamp to datetime
data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# Set the Timestamp as the index
data.set_index('Timestamp', inplace=True)

# Resample data to hourly average
hourly_data = data['AQI'].resample('h').mean()

# Convert Series to DataFrame
hourly_data = hourly_data.to_frame(name='AQI')

# Interpolate missing values to handle any gaps due to resampling
hourly_data = hourly_data.interpolate()

# Create lag features for the last 24 hours to use for prediction
for lag in range(1, 25):
    hourly_data[f'lag_{lag}'] = hourly_data['AQI'].shift(lag)

# Drop the rows with NaN values resulting from lag feature creation
hourly_data = hourly_data.dropna()

# Split the data into features (X) and target (y)
X = hourly_data.drop('AQI', axis=1)
y = hourly_data['AQI']

# Split the data into training and testing sets (80% training, 20% testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create the Random Forest model
model = RandomForestRegressor(n_estimators=100, random_state=42)

# Train the model
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Test Set Mean Squared Error: {mse}")
print(f"Test Set R-squared: {r2}")

# Forecast the next 24 hours
last_row = hourly_data[-1:].drop('AQI', axis=1)
forecast = []
for i in range(24):
    pred = model.predict(last_row)
    forecast.append(pred[0])
    new_row = pd.Series([pred[0]] + list(last_row.iloc[0, :-1]), index=last_row.columns)
    last_row = pd.DataFrame([new_row])

# Create a DataFrame for the predictions
forecast_df = pd.DataFrame({'hour': range(24), 'predicted_AQI': np.round(forecast, 2)})

# Print the lowest and highest AQI from the source data
lowest_aqi = data['AQI'].min()
lowest_aqi_time = data['AQI'].idxmin()
highest_aqi = data['AQI'].max()
highest_aqi_time = data['AQI'].idxmax()

print(f"Lowest AQI: {lowest_aqi} at {lowest_aqi_time}")
print(f"Highest AQI: {highest_aqi} at {highest_aqi_time}")

# Print the forecasted AQI values
print(forecast_df.to_string(index=False))

# Save the forecast to a CSV file
forecast_df.to_csv('forecasted_aqi.csv', index=False)
