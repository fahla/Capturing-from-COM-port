# Capturing-from-COM-port

master_script.py
The master script captures environmental data from a serial port, uploads it to an FTP server, performs peak hour analysis, generates AQI data, and makes predictions using a Random Forest model. It handles data collection, processing, and uploading in a continuous loop with error handling and retry mechanisms. Additionally, it performs initial model predictions and uploads the results.

peak_hour_common.py
This script calculates AQI from sensor data, performs peak hour analysis, interpolates missing hours, and saves the results. It reads data from a CSV, filters it by a date range, and calculates AQI for PM2.5 and PM10. The script keeps the last 24 hourly entries, ensures accurate peak hour indicators, and handles missing data via linear interpolation. Finally, it saves the processed data to a CSV file.

random_forest.py
This script forecasts AQI values using a Random Forest model. It preprocesses the data to create lag features, trains the model with historical AQI data, and generates predictions for the next 24 hours. The predicted hourly AQI values are saved to a CSV file, ensuring the model is robust and handles potential preprocessing issues.

prediction_model.py (not used in latest version)
This script calculates AQI for PM2.5 and PM10 from sensor data, resamples the data to an hourly frequency, and prepares it for forecasting using the Prophet model. It makes future predictions for the next 24 hours, ensuring non-negative values, and calculates the mean predicted AQI for each hour. The predicted hourly AQI values are saved to a CSV file.


We have also tried lstm, prophet model and arima however random forest has yielded most reliable data.





