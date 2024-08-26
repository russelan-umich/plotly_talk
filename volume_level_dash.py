import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objs as go
import pyaudio
import numpy as np
import threading
import time

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
        html.Button('Start', id='start-button', n_clicks=0, className='button'),
        className='button-container'
    )
])

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
        volume_db = 20 * np.log10(volume)
        volume_data.append(volume_db)
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

# Callback to update the graph
@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals')]
)
def update_graph(n_intervals):
    global volume_data

    # Generate a list that goes from 33 to 3
    seconds_since_list = list(range(33, 3, -1))

    data = go.Scatter(
        x=seconds_since_list,
        y=volume_data,
        mode='lines+markers'
    )
    
    layout = go.Layout(
        xaxis=dict(title='Seconds Ago', range=[33, 3]),
        yaxis=dict(title='Volume (db)',range=[min(volume_data) if volume_data else -1, max(volume_data) if volume_data else 1])
    )

    return {'data': [data], 'layout': go.Layout(layout)}

if __name__ == '__main__':
    app.run_server(debug=True, port=8002)