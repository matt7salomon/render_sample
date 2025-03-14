import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__)

# Generate dataset
np.random.seed(42)
num_panelists = 40
data = {
    "Panelist_ID": [f"P{i+1}" for i in range(num_panelists)],
    "Response_Rate": np.clip(np.random.uniform(0.1, 0.3, num_panelists) + np.random.choice([0, 0.5], num_panelists, p=[0.9, 0.1]), 0, 1),
    "Abandon_Rate": np.clip(np.random.uniform(0, 0.2, num_panelists), 0, 1),
    "Non_Profane_Rate": np.clip(np.random.uniform(0.8, 1, num_panelists), 0, 1),
    "Non_Speed_Rate": np.clip(np.random.uniform(0.8, 1, num_panelists), 0, 1),
}
df = pd.DataFrame(data)

# Define the app layout
app.layout = html.Div([
    html.H1("Panelist Health Score Dashboard"),
    
    # Sliders for weight adjustment
    html.Label("Response Rate Weight"),
    dcc.Slider(id='weight-response', min=0, max=1, step=0.01, value=0.4, marks={0: '0', 0.5: '0.5', 1: '1'}),
    
    html.Label("Abandon Rate Weight"),
    dcc.Slider(id='weight-abandon', min=-1, max=0, step=0.01, value=-0.2, marks={-1: '-1', -0.5: '-0.5', 0: '0'}),
    
    html.Label("Non-Profane Rate Weight"),
    dcc.Slider(id='weight-non-profane', min=0, max=1, step=0.01, value=0.3, marks={0: '0', 0.5: '0.5', 1: '1'}),
    
    html.Label("Non-Speed Rate Weight"),
    dcc.Slider(id='weight-non-speed', min=0, max=1, step=0.01, value=0.3, marks={0: '0', 0.5: '0.5', 1: '1'}),
    
    html.Br(),
    html.H3("Updated Health Scores"),
    dcc.Graph(id='health-score-bar-chart'),
    
    html.H3("Community Health Score", style={'marginTop': '20px'}),
    html.Div(id='community-health-score', style={'fontSize': '32px', 'fontWeight': 'bold', 'textAlign': 'center'})
])

# Callback to update health score and chart
@app.callback(
    [Output('health-score-bar-chart', 'figure'),
     Output('community-health-score', 'children')],
    [Input('weight-response', 'value'),
     Input('weight-abandon', 'value'),
     Input('weight-non-profane', 'value'),
     Input('weight-non-speed', 'value')]
)
def update_chart(w1, w2, w3, w4):
    df["Health_Score"] = (
        df["Response_Rate"] * w1 +
        df["Abandon_Rate"] * w2 +
        df["Non_Profane_Rate"] * w3 +
        df["Non_Speed_Rate"] * w4
    )
    df["Health_Score"] = (df["Health_Score"] - df["Health_Score"].min()) / (df["Health_Score"].max() - df["Health_Score"].min())
    
    community_health_score = df["Health_Score"].mean()
    
    fig = px.bar(df, x="Panelist_ID", y="Health_Score", title="Panelist Health Scores", labels={"Health_Score": "Score"},
                 color="Health_Score", color_continuous_scale="Viridis")
    
    return fig, f"Average Health Score: {community_health_score:.2f}"

# Run the app
server = app.server  # This exposes the Flask server instance to Gunicorn

if __name__ == '__main__':
    app.run_server(debug=True)
