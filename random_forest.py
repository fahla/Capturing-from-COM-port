import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def forecast_aqi(input_file, output_file):
    # Load the data
    data = pd.read_csv(input_file)

    # Convert date and hour to datetime
    data['Timestamp'] = pd.to_datetime(data['date'] + ' ' + data['hour'].astype(str) + ':00:00')

    # Set the Timestamp as the index
    data.set_index('Timestamp', inplace=True)

    # Use 'overall_aqi_mean' as the AQI value
    data['AQI'] = data['overall_aqi_mean']

    # Drop unnecessary columns
    data = data[['AQI']]

    # Resample data to hourly average (This step might not be necessary if the data is already hourly)
    hourly_data = data['AQI'].resample('H').mean()

    # Convert Series to DataFrame
    hourly_data = hourly_data.to_frame(name='AQI')

    # Display initial data info
    print("Initial data after resampling and before adding lag features:")
    print(hourly_data.info())
    print(hourly_data.head())

    # Create lag features for the last 24 hours to use for prediction
    max_lag = 24  # Maximum number of lag features
    for lag in range(1, max_lag + 1):
        hourly_data[f'lag_{lag}'] = hourly_data['AQI'].shift(lag)

    # Drop the rows with NaN values resulting from lag feature creation
    hourly_data = hourly_data.dropna()

    # Display data info after processing
 #   print("Data after adding lag features and dropping NaN values:")
  #  print(hourly_data.info())
 #   print(hourly_data.head())

    # Check if the processed data is sufficient
    if hourly_data.shape[0] == 0:
        raise ValueError("The processed dataset is empty after dropping NaN values. Please check the data and preprocessing steps.")

    # Split the data into features (X) and target (y)
    X = hourly_data.drop('AQI', axis=1)
    y = hourly_data['AQI']

    # Split the data into training and testing sets (80% training, 20% testing)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=59)

    # Check if the train and test sets are not empty
    if X_train.shape[0] == 0 or X_test.shape[0] == 0:
        raise ValueError("The train or test set is empty. Adjust the test_size parameter or check the data.")

    # Create the Random Forest model
    model = RandomForestRegressor(n_estimators=100, random_state=42)

    # Train the model
    model.fit(X_train, y_train)

    # Predict on the test set
    y_pred = model.predict(X_test)
  #  print(f"Test Set Mean Squared Error: {mean_squared_error(y_test, y_pred)}")

    # Forecast the next 24 hours
    last_row = hourly_data[-1:].drop('AQI', axis=1)
    forecast = []
    for i in range(24):
        pred = model.predict(last_row)
        forecast.append(pred[0])
        new_row = pd.Series([pred[0]] + list(last_row.iloc[0, :-1]), index=last_row.columns)
        last_row = pd.DataFrame([new_row])

    # Create a DataFrame for the predictions
    forecast_df = pd.DataFrame({'hour': range(24), 'predicted_AQI': np.round(forecast)})

    # Print the lowest and highest AQI from the source data
    lowest_aqi = data['AQI'].min()
    lowest_aqi_time = data['AQI'].idxmin()
    highest_aqi = data['AQI'].max()
    highest_aqi_time = data['AQI'].idxmax()

   # print(f"Lowest AQI: {lowest_aqi} at {lowest_aqi_time}")
   # print(f"Highest AQI: {highest_aqi} at {highest_aqi_time}")

    # Print the forecasted AQI values
  #  print(forecast_df.to_string(index=False))

    # Save the forecast to a CSV file
    forecast_df.to_csv(output_file, index=False)

# Example usage
# forecast_aqi('input_file.csv', 'output_file.csv')
