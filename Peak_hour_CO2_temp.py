import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the CSV file
file_path = 'C:/sensor/sensor_data_kitchen.csv'
data = pd.read_csv(file_path, encoding='latin1')

# Convert the 'Timestamp' column to datetime format
data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# Plot for CO2 (ppm)
fig_co2 = px.line(
    data, 
    x='Timestamp', 
    y='CO2 (ppm)', 
    title='CO2 Dynamics Over Time',
    labels={'CO2 (ppm)': 'CO2 (ppm)', 'Timestamp': 'Timestamp'},
    hover_data={'Timestamp': '|%Y-%m-%d %H:%M:%S'}
)

# Identify the peak CO2 value
peak_co2 = data.loc[data['CO2 (ppm)'].idxmax()]

# Add a marker for the peak CO2 value
fig_co2.add_trace(
    go.Scatter(
        x=[peak_co2['Timestamp']], 
        y=[peak_co2['CO2 (ppm)']], 
        mode='markers+text', 
        name='Peak CO2',
        text=[f'Peak: {peak_co2["CO2 (ppm)"]} ppm'],
        textposition='top right',
        marker=dict(color='red', size=10)
    )
)

# Update layout
fig_co2.update_layout(
    xaxis_title='Timestamp',
    yaxis_title='CO2 (ppm)',
    hovermode='x unified'
)

# Plot for Temperature (°C)
fig_temp = px.line(
    data, 
    x='Timestamp', 
    y='Temperature (°C)', 
    title='Temperature Dynamics Over Time',
    labels={'Temperature (°C)': 'Temperature (°C)', 'Timestamp': 'Timestamp'},
    hover_data={'Timestamp': '|%Y-%m-%d %H:%M:%S'}
)

# Identify the peak Temperature value
peak_temp = data.loc[data['Temperature (°C)'].idxmax()]

# Add a marker for the peak Temperature value
fig_temp.add_trace(
    go.Scatter(
        x=[peak_temp['Timestamp']], 
        y=[peak_temp['Temperature (°C)']], 
        mode='markers+text', 
        name='Peak Temperature',
        text=[f'Peak: {peak_temp["Temperature (°C)"]} °C'],
        textposition='top right',
        marker=dict(color='red', size=10)
    )
)

# Update layout
fig_temp.update_layout(
    xaxis_title='Timestamp',
    yaxis_title='Temperature (°C)',
    hovermode='x unified'
)

# Create a new DataFrame for peak values
peak_values = pd.DataFrame({
    'Metric': ['CO2', 'Temperature'],
    'Value': [peak_co2['CO2 (ppm)'], peak_temp['Temperature (°C)']],
    'Timestamp': [peak_co2['Timestamp'], peak_temp['Timestamp']]
})

# Save the peak values to a CSV file
output_file_path = 'C:/sensor/peak_values.csv'
peak_values.to_csv(output_file_path, index=False)

# Show the plots
fig_co2.show()
fig_temp.show()

# Assuming top_peak_hours is a DataFrame with peak hour analysis results
top_peak_hours = peak_values  # Replace this with your actual peak hour analysis DataFrame

# Define the output CSV file path for the peak hour analysis results
output_csv_file = 'C:/sensor/top_peak_hours.csv'

# Save the peak hour analysis results to a CSV file
top_peak_hours.to_csv(output_csv_file, index=False)
