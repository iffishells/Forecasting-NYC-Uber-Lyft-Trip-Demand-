import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import glob
# Load the DataFrame and preprocess the data
data_list_path = glob.glob('Datasets/fhv_tripdata_2022-2023_in_csv/*.csv')
list_df = []
for path in data_list_path:
    df = pd.read_csv(path)
    list_df.append(df)
df = pd.concat(list_df)
interested_features = ['pickup_datetime', 'PUlocationID']
df = df[interested_features]
removed_nan_df = df.dropna()

# Get unique PUlocationIDs
location_ids = removed_nan_df['PUlocationID'].unique().tolist()

# Create the Dash app
app = dash.Dash(__name__)

# Set up the layout
app.layout = html.Div([
    html.H1('Pickup Analysis Dashboard'),
    html.Div([
        html.Label('Select PUlocationID:'),
        dcc.Dropdown(
            id='location-dropdown',
            options=[{'label': str(loc_id), 'value': loc_id} for loc_id in location_ids],
            value=location_ids[0]
        )
    ]),
    html.Div(id='output-graph')
])

# Define the callback function to update the graph based on the selected PUlocationID
@app.callback(
    Output('output-graph', 'children'),
    [Input('location-dropdown', 'value')]
)
def update_graph(location_id):
    # Filter the DataFrame based on the selected PUlocationID
    df_subset = removed_nan_df[removed_nan_df['PUlocationID'] == location_id]
    df_subset['pickup_datetime'] = pd.to_datetime(df_subset['pickup_datetime'])
    df_subset = df_subset.sort_values('pickup_datetime')

    # Resample the data to get pickups per hour
    df_subset = df_subset.resample('1H', on='pickup_datetime').count()

    # Create the line plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_subset.index, y=df_subset['PUlocationID'], mode='lines+markers', name='Pickups per Hour'))

    # Update the layout
    fig.update_layout(
        title=f'Pickups per Hour for PUlocationID {location_id}',
        xaxis_title='pickup_datetime',
        yaxis_title='Pickups per Hour'
    )

    # Return the graph component to be displayed
    return dcc.Graph(figure=fig)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
