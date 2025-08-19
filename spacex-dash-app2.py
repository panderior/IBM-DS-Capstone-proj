# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import os

REPO_URL = "https://github.com/panderior/IBM-DS-Capstone-proj"
REPORT_URL = "https://github.com/panderior/IBM-DS-Capstone-proj/blob/main/report/ds-capstone-report-coursera.pdf"

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("data/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

site_fullname_map = {
    "CCAFS LC-40": "Cape Canaveral AFS LC-40",
    "CCAFS SLC-40": "Cape Canaveral AFS SLC-40",
    "KSC LC-39A": "Kennedy Space Center LC-39A",
    "VAFB SLC-4E": "Vandenberg AFB SLC-4E",
}
spacex_df["Launch Site (Full)"] = spacex_df["Launch Site"].map(site_fullname_map).fillna(spacex_df["Launch Site"])

# Create a dash application
app = dash.Dash(__name__)
app.title = "SpaceX Launch Records Dashboard"

site_options = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": site_fullname_map[k], "value": k} for k in site_fullname_map
]

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "fontSize": 40},
        ),

        # ---------------- About block (top description) ----------------
        dcc.Markdown(
            """
### Welcome
This dashboard lets you explore **SpaceX Falcon 9** launch outcomes. Use the controls below to filter by **launch site** and **payload mass** and see how they relate to mission success.

**What’s here**
- **Success breakdown (pie chart):** Shows *how many successful launches* occurred by site.  
- **Payload vs. success (scatter):** Shows the relationship between **payload mass** and **landing outcome**, colored by **booster version**.

**How to interact**

1. **Launch Site selector** – Choose a specific site or **All Sites**.  
2. **Payload range slider** – Drag the handles to focus on payloads of interest.  
3. **Hover** on points or slices for exact values; **legend clicks** let you isolate/compare traces.

**What insights to look for**
- Which sites contribute most to successful missions?  
- Do heavier payloads reduce success rates—or is the effect minimal?  
- Are certain **booster versions** consistently successful in specific payload ranges?

**Links**
- 📦 **Repository:** [GitHub repo ↗](""" + REPO_URL + """)
- 📄 **Report:** [Project report ↗](""" + REPORT_URL + """)
            """,
            style={"maxWidth": 1100, "margin": "0 auto 1rem", "lineHeight": "1.4"},
        ),

        # -------------- Controls --------------
        html.Label("Launch Site", style={"fontWeight": 600}),
        dcc.Dropdown(
            id="site-dropdown",
            options=site_options,
            value="ALL",
            placeholder="Select a Launch Site here",
            searchable=True,
            clearable=False,
            style={"maxWidth": 500},
        ),
        html.Br(),

        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),

        html.Label("Payload range (kg)", style={"fontWeight": 600}),
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            value=[min_payload, max_payload],
            tooltip={"placement": "bottom", "always_visible": False},
        ),
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ],
    style={"padding": "20px"},
)

# ---------------- Callbacks ----------------
@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        fig = px.pie(
            spacex_df,
            values="class",
            names="Launch Site (Full)",
            title="Total Successful Launches by Site",
        )
    else:
        temp_data = spacex_df[spacex_df["Launch Site"] == entered_site]
        counts = (
            temp_data["class"]
            .value_counts()
            .reset_index(name="count")
            .rename(columns={"index": "class"})
        )
        fig = px.pie(
            counts,
            values="count",
            names="class",
            title=f"Success vs. Failure – {site_fullname_map.get(entered_site, entered_site)}",
        )
    return fig


@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def get_scatter_chart(entered_site, payload_range):
    min_p, max_p = payload_range

    if entered_site == "ALL":
        dff = spacex_df.copy()
        site_label = "All Sites"
    else:
        dff = spacex_df[spacex_df["Launch Site"] == entered_site]
        site_label = site_fullname_map.get(entered_site, entered_site)

    mask = (dff["Payload Mass (kg)"] >= min_p) & (dff["Payload Mass (kg)"] <= max_p)
    dff = dff[mask]

    fig = px.scatter(
        dff,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version",
        hover_data={"Launch Site (Full)": True, "Payload Mass (kg)": True, "class": True},
        title=f"Payload vs. Launch Success – {site_label}",
        labels={"class": "Landing Success (1=yes, 0=no)"},
    )
    return fig


# Run the app
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8050))
    host = os.getenv("HOST", "0.0.0.0")
    app.run_server(host=host, port=port)


# # Import required libraries
# import pandas as pd
# import dash
# from dash import html
# from dash import dcc
# from dash.dependencies import Input, Output
# import plotly.express as px
# import os

# # Read the airline data into pandas dataframe
# spacex_df = pd.read_csv("data/spacex_launch_dash.csv")
# max_payload = spacex_df['Payload Mass (kg)'].max()
# min_payload = spacex_df['Payload Mass (kg)'].min()

# # Create a dash application
# app = dash.Dash(__name__)

# # Create an app layout
# app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
#                                         style={'textAlign': 'center', 'color': '#503D36',
#                                                'font-size': 40}),
#                                 # TASK 1: Add a dropdown list to enable Launch Site selection
#                                 # The default select value is for ALL sites
#                                 dcc.Dropdown(
#                                     id='site-dropdown',
#                                     options=[
#                                         {'label': 'All Sites', 'value': 'ALL'},
#                                         {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
#                                         {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
#                                         {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
#                                         {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
#                                     ],
#                                     value='ALL',
#                                     placeholder="Select a Launch Site here",
#                                     searchable=True
#                                 ),
#                                 html.Br(),

#                                 # TASK 2: Add a pie chart to show the total successful launches count for all sites
#                                 # If a specific launch site was selected, show the Success vs. Failed counts for the site
#                                 html.Div(dcc.Graph(id='success-pie-chart')),
#                                 html.Br(),

#                                 html.P("Payload range (Kg):"),
#                                 # TASK 3: Add a slider to select payload range
#                                 dcc.RangeSlider(
#                                     id='payload-slider',
#                                     min=0, max=10000, step=1000,
#                                     # marks={0: '0', 100: '100'},
#                                     value=[min_payload, max_payload]
#                                 ),

#                                 # TASK 4: Add a scatter chart to show the correlation between payload and launch success
#                                 html.Div(dcc.Graph(id='success-payload-scatter-chart')),
#                                 ])

# # TASK 2:
# # Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# # Function decorator to specify function input and output
# @app.callback(Output(component_id='success-pie-chart', component_property='figure'),
#               Input(component_id='site-dropdown', component_property='value'))
# def get_pie_chart(entered_site):
#     filtered_df = spacex_df
#     if entered_site == 'ALL':
#         fig = px.pie(
#             spacex_df, 
#             values='class', 
#             names='Launch Site', 
#             title='Total Success Launches By Site'
#         )
#     else:
#         # return the outcomes piechart for a selected site
#         temp_data = spacex_df[spacex_df['Launch Site']==entered_site]
#         counts = (
#             temp_data['class']
#             .value_counts()                           
#             .reset_index(name='count')                
#             .rename(columns={'index':'class'})        
#         )
        
#         # print(temp_data['class'].head())
#         fig = px.pie(
#             counts,
#             values='count',      # the counts of each outcome
#             names='class',   
#             title=f'Total Success Launches By Site - {entered_site}'
#         )
#     return fig

# # TASK 4:
# # Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# @app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
#                 [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")]
# )
# def get_scatter_chart(entered_site, payload_range):
#     # 1) unpack the slider values
#     min_payload, max_payload = payload_range

#     # 2) filter by site
#     if entered_site == 'ALL':
#         dff = spacex_df.copy()
#     else:
#         dff = spacex_df[spacex_df['Launch Site'] == entered_site]

#     # 3) filter by payload using & and parentheses
#     mask = (
#         (dff['Payload Mass (kg)'] >= min_payload) &
#         (dff['Payload Mass (kg)'] <= max_payload)
#     )
#     dff = dff[mask]

#     # 4) build your scatter (example)
#     fig = px.scatter(
#         dff,
#         x='Payload Mass (kg)',
#         y='class',
#         color='Booster Version',
#         title=f'Payload vs. Success for {entered_site}'
#     )
#     return fig


# # Run the app
# if __name__ == '__main__':
#     port = int(os.getenv('PORT', 8050))
#     host = os.getenv('HOST', '0.0.0.0')
#     app.run_server(host=host, port=port)
