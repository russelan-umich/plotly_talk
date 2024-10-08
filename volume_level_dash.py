import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objs as go
import numpy as np
import threading
import pyaudio
import random
import string
import time
import csv

# External CSS Stylesheet
external_stylesheets = [dbc.themes.BOOTSTRAP, 'assets/volume_level_dash.css']                                            

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Layout of the app
app.layout = html.Div([
    html.H1("Microphone Volume Plot", className='header'),
    dcc.Graph(id='live-graph', animate=True),
    dcc.Interval(id='graph-update', interval=1000, n_intervals=0),
    html.Div(
        [
            html.Button('Start', id='start-button', n_clicks=0, className='button'),
            html.Button('Download', id='download-button', n_clicks=0, className='blue-button'),
            dcc.Download(id='download-data')
        ],
        className='button-container'
    )
])

# Save a server object for running the app
server = app.server

# Global variables to store audio data
volume_data = []
start_recording = False

# Function to capture audio from the microphone
def audio_listener():
    global volume_data, start_recording
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    while start_recording:
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        volume = np.linalg.norm(data) / CHUNK
        volume_data.append(volume)
        if len(volume_data) > 30:
            volume_data.pop(0)
        time.sleep(1)

    stream.stop_stream()
    stream.close()
    p.terminate()

# Callback to start the audio listener thread
@app.callback(
    Output('start-button', 'children'),
    [Input('start-button', 'n_clicks')]
)
def start_audio_listener(n_clicks):
    global start_recording
    if n_clicks % 2 == 0:
        start_recording = False
        return "Start"
    else:
        start_recording = True
        threading.Thread(target=audio_listener).start()
        return "Stop"
    
# Callback to download the volume data
@app.callback(
    Output('download-data', 'data'),
    [Input('download-button', 'n_clicks')]
)
def download_volume_data(n_clicks):
    if n_clicks:
        # Allow user to download the volume data
        random_string = ''.join(random.choices(string.digits, k=10))
        csv_file = f'volume_data_{random_string}.csv'
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Volume'])
            writer.writerows(zip(volume_data))
        return dcc.send_file(csv_file, csv_file)

# Callback to update the graph
@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals')]
)
def update_graph(n_intervals):
    global volume_data

    # Generate a list that goes from 3 to 33
    seconds_since_list = list(range(3, 33, 1))

    # Reverse the volume data to plot the most recent data on the right
    volume_data_reverse = volume_data[::-1]

    data = go.Scatter(
        x=seconds_since_list,
        y=volume_data_reverse,
        mode='lines+markers'
    )
    
    layout = go.Layout(
        xaxis=dict(title='Seconds Ago', range=[33, 3]),
        yaxis=dict(title='Normalized Volume',range=[min(volume_data) if volume_data else -1, max(volume_data) if volume_data else 1])
    )

    return {'data': [data], 'layout': go.Layout(layout)}

if __name__ == '__main__':
    app.run_server(debug=True, port=8003)