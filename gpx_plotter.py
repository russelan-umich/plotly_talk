'''
Plot a GPX file on a map using Dash
'''

# Import packages
from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import gpxpy

# Read gpx file
gpx = gpxpy.parse(open("sample_run.gpx"))

# Initialize the app
app = Dash()

# App layout
app.layout = html.Div([
    html.Div(children='GPX Plotter'),
    html.Hr(),
    dcc.Graph(
        id="gpxGraph",
        style={
                'height': '600px',
                'width': '100%',
                'backgroundColor': '#f2f2f2',
                'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)', 
            }
    )

])

# Plot the GPX data onto a map on gpxGraph
@app.callback(
    Output('gpxGraph', 'figure'),
    Input('gpxGraph', 'id')
)
def plot_gpx_data(id):
    # Get the latitude and longitude data
    data = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data.append({
                    "lat": point.latitude,
                    "lon": point.longitude
                })

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Create an empty scatterbox with the street map as a background
    gpx_plot = go.Figure()
    gpx_plot.add_trace(go.Scattermapbox())
    gpx_plot.update_layout(
        mapbox_style='open-street-map'
    )

    gpx_plot.update_layout(
            mapbox_center_lon=df['lon'].mean(), 
            mapbox_center_lat=df['lat'].mean(),
            mapbox_zoom=13, 
            title={'text': f'Sample GPX Plot', 
                   'xanchor' : 'left', 
                   'yanchor' : 'top',
            }
                
        )
    
    # Addd the GPX data to the map
    gpx_plot.add_trace(go.Scattermapbox(
        lon=df['lon'],
        lat=df['lat'],
        opacity=1,
        name='GPX Point',
        showlegend=False
    ))

    return gpx_plot


# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8002)