# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import os
import json
import datetime
from flask import request

REPO_URL = "https://github.com/panderior/IBM-DS-Capstone-proj"
REPORT_URL = "https://github.com/panderior/IBM-DS-Capstone-proj/blob/main/report/ds-capstone-report-coursera.pdf"
AUTHOR_GITHUB_URL = "https://github.com/panderior"
AUTHOR_LINKEDIN_URL = "https://www.linkedin.com/in/duguma-yeshitla/"
LOG_FILE = "daily_counts.json"

# helper functions
def _load_counts():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {}  

def _save_counts(counts):
    with open(LOG_FILE, "w") as f:
        json.dump(counts, f)

def get_today_count():
    today = datetime.date.today().isoformat()
    counts = _load_counts()
    return int(counts.get(today, 0))

# Read the data
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

# App
app = dash.Dash(__name__)
app.title = "SpaceX Launch Records Dashboard"

# Options for dropdown (full names as labels, raw codes as values)
site_options = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": site_fullname_map[k], "value": k} for k in site_fullname_map
]

# ---------- LAYOUT ----------
def serve_layout():
    return html.Div(
            children=[
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("ibm_ds_logo.jpeg"),
                            alt="IBM Data Science badge",
                            style={
                                "height": "72px",     
                                "width": "auto",
                                "display": "block",
                            },
                        ),
                        html.H1(
                            "SpaceX Launch Records Dashboard",
                            style={
                                "margin": 0,
                                "color": "#503D36",
                                "fontSize": 40,
                                "lineHeight": "1.1",
                                "textAlign": "left",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center", 
                        "gap": "16px",
                        "marginBottom": "8px",
                        "flexWrap": "wrap",        
                    },
                ),

                # --------- Collapsible "About" panel (collapsed by default) ----------
                html.Details(
                    open=False,  
                    children=[
                        html.Summary(
                            "About this dashboard (click to expand)",
                            style={
                                "cursor": "pointer",
                                "fontWeight": 600,
                                "listStyle": "none",
                                "outline": "none",
                                "textAlign": "center",   
                                "fontSize": "18px",
                            },
                        ),
                        html.Div(
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

                                **Author**
                                - Duguma Y. (panderior): [LinkedIn ↗](""" + AUTHOR_LINKEDIN_URL + """) | [GitHub ↗](""" + AUTHOR_GITHUB_URL + """)

                                **Today's visits**: """ + str(get_today_count()) + """
                                """
                            ),
                            style={
                                "background": "#f8f8f8",
                                "border": "1px solid #e6e6e6",
                                "padding": "16px",
                                "borderRadius": "10px",
                                "marginTop": "10px",
                                "maxWidth": 1100,
                            },
                        ),
                    ],
                    style={"maxWidth": 1100, "margin": "0 auto 1rem"},
                ),
                html.Br(),
                # -------------- Controls --------------
                html.Div(
                    children=[
                        html.Label("Launch Site", style={"fontWeight": 600, "display": "block", "marginBottom": "8px"}),
                        dcc.Dropdown(
                            id="site-dropdown",
                            options=site_options,
                            value="ALL",
                            placeholder="Select a Launch Site here",
                            searchable=True,
                            clearable=False,
                            style={"width": "60%", "margin": "0 auto"}, 
                        ),
                    ],
                    style={"textAlign": "center", "marginBottom": "20px"},
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
            style={"padding": "20px", "margin": "40px"},
        )

app.layout = serve_layout

# ---------- CALLBACKS ----------
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        return px.pie(
            spacex_df,
            values="class",
            names="Launch Site (Full)",
            title="Total Successful Launches by Site",
        )
    temp = spacex_df[spacex_df["Launch Site"] == entered_site]
    counts = (
        temp["class"].value_counts().reset_index(name="count").rename(columns={"index": "class"})
    )
    return px.pie(
        counts,
        values="count",
        names="class",
        title=f"Success vs. Failure – {site_fullname_map.get(entered_site, entered_site)}",
    )

@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [Input("site-dropdown", "value"), Input("payload-slider", "value")],
)
def get_scatter_chart(entered_site, payload_range):
    min_p, max_p = payload_range
    dff = spacex_df if entered_site == "ALL" else spacex_df[spacex_df["Launch Site"] == entered_site]
    dff = dff[(dff["Payload Mass (kg)"] >= min_p) & (dff["Payload Mass (kg)"] <= max_p)]
    site_label = "All Sites" if entered_site == "ALL" else site_fullname_map.get(entered_site, entered_site)
    return px.scatter(
        dff,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version",
        hover_data={"Launch Site (Full)": True, "Payload Mass (kg)": True, "class": True},
        title=f"Payload vs. Launch Success – {site_label}",
        labels={"class": "Landing Success (1=yes, 0=no)"},
    )

@app.server.before_request
def log_daily_access():
    # Only count real page loads that return HTML
    if request.method != "GET":
        return

    path = request.path or "/"
    if (
        path.startswith("/_dash-") or
        path.startswith("/assets/") or
        path == "/favicon.ico"
    ):
        return

    accept = request.headers.get("Accept", "")
    if "text/html" not in accept:
        return  # ignore JSON/XHR, images, etc.

    # Some browsers/XHR set this; be explicit
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return

    # Passed all filters → count it
    today = datetime.date.today().isoformat()
    counts = _load_counts()
    counts[today] = int(counts.get(today, 0)) + 1
    _save_counts(counts)


# Run the app
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8050))
    host = os.getenv("HOST", "0.0.0.0")
    app.run_server(host=host, port=port)
