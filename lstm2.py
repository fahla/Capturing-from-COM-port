import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# Load the data
file_path = 'sensor_data_aqi.csv'
data = pd.read_csv(file_path)

# Convert Timestamp to datetime
data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# Set the Timestamp as the index
data.set_index('Timestamp', inplace=True)

# Resample data to hourly average
hourly_data = data['AQI'].resample('H').mean().interpolate()

# Convert the data to a numpy array and scale it
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(hourly_data.values.reshape(-1, 1))

# Define the time step for the LSTM
time_step = 24

# Create the training dataset
train_data = []
for i in range(time_step, len(scaled_data) - 24):
    train_data.append(scaled_data[i-time_step:i, 0])

train_data = np.array(train_data)

# Split into input (X) and output (y)
X_train = train_data[:-24]
y_train = scaled_data[time_step:-24, 0]

# Convert to torch tensors
X_train = torch.from_numpy(X_train).float()
y_train = torch.from_numpy(y_train).float()

# Reshape input to be [samples, time steps, features]
X_train = X_train.unsqueeze(2)

# Define the LSTM model
class LSTMModel(nn.Module):
    def __init__(self):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=50, num_layers=2, batch_first=True)
        self.fc = nn.Linear(50, 1)

    def forward(self, x):
        h_0 = torch.zeros(2, x.size(0), 50)
        c_0 = torch.zeros(2, x.size(0), 50)
        out, _ = self.lstm(x, (h_0, c_0))
        out = self.fc(out[:, -1, :])
        return out

# Instantiate the model, define the loss function and the optimizer
model = LSTMModel()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Train the model
num_epochs = 100
for epoch in range(num_epochs):
    model.train()
    outputs = model(X_train)
    optimizer.zero_grad()
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()
    if (epoch+1) % 10 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

# Create the testing dataset
test_data = scaled_data[len(scaled_data) - 24 - time_step:, :]

# Create the datasets x_test and y_test
X_test = []
for i in range(time_step, len(test_data)):
    X_test.append(test_data[i-time_step:i, 0])

# Convert to numpy array and to torch tensor
X_test = np.array(X_test)
X_test = torch.from_numpy(X_test).float()
X_test = X_test.unsqueeze(2)

# Get the models predicted price values
model.eval()
with torch.no_grad():
    predictions = model(X_test).numpy()

predictions = scaler.inverse_transform(predictions)

# Create a DataFrame for the predictions
forecast_index = pd.date_range(start=hourly_data.index[-1] + pd.Timedelta(hours=1), periods=24, freq='H')
forecast_df = pd.DataFrame({'Timestamp': forecast_index, 'Predicted AQI': predictions.flatten()})

# Format the Timestamp for better readability
forecast_df['Hour'] = forecast_df['Timestamp'].dt.strftime('%I:%M %p')
forecast_df = forecast_df[['Hour', 'Predicted AQI']]

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
