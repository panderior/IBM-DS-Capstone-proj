# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import os

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("data/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                    ],
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                ),
                                html.Br(),

                                # Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    # marks={0: '0', 100: '100'},
                                    value=[min_payload, max_payload]
                                ),

                                # Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df, 
            values='class', 
            names='Launch Site', 
            title='Total Success Launches By Site'
        )
    else:
        # return the outcomes piechart for a selected site
        temp_data = spacex_df[spacex_df['Launch Site']==entered_site]
        counts = (
            temp_data['class']
            .value_counts()                           
            .reset_index(name='count')                
            .rename(columns={'index':'class'})        
        )
        
        # print(temp_data['class'].head())
        fig = px.pie(
            counts,
            values='count',      # the counts of each outcome
            names='class',   
            title=f'Total Success Launches By Site - {entered_site}'
        )
    return fig

# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
                [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_chart(entered_site, payload_range):
    # unpack the slider values
    min_payload, max_payload = payload_range

    # filter by site
    if entered_site == 'ALL':
        dff = spacex_df.copy()
    else:
        dff = spacex_df[spacex_df['Launch Site'] == entered_site]

    # filter by payload using & and parentheses
    mask = (
        (dff['Payload Mass (kg)'] >= min_payload) &
        (dff['Payload Mass (kg)'] <= max_payload)
    )
    dff = dff[mask]

    # build your scatter (example)
    fig = px.scatter(
        dff,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version',
        title=f'Payload vs. Success for {entered_site}'
    )
    return fig


# Run the app
if __name__ == '__main__':
    port = int(os.getenv('PORT', 8050))
    host = os.getenv('HOST', '0.0.0.0')
    app.run_server(host=host, port=port)
