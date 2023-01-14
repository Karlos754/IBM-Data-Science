# Import required libraries
import pandas as pd
# import dash
# import dash_html_components as html
# import dash_core_components as dcc
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# extract `Launch Sites` to list of dicts
launch_sites_diclist = [{'label': 'All sites', 'value': 'ALL'}]
launch_sites_diclist.extend([{'label': x, 'value': x} for x in spacex_df['Launch Site'].unique().tolist()])

# Create a dash application
app = Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                    options=launch_sites_diclist,
                                    value='ALL',
                                    placeholder='Select Launch Site',
                                    searchable=True
                                ),

                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                    min=0,
                                    max=spacex_df['Payload Mass (kg)'].max().astype(np.int64),
                                    step=1000,
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
)
def get_pie_chart(launch_site):
    df = spacex_df[['Launch Site', 'class']]

    if launch_site == 'ALL':
        fig = px.pie(df, values='class', names='Launch Site', title='Total launches')
        return fig
    else:
        fig = px.pie(
            # df[df['Launch Site']==launch_site]['class'].value_counts(),
            df[df['Launch Site']==launch_site].groupby(['class']).count().reset_index(),
            values='Launch Site',
            names='class',
            title=f'Successful launches rate for {launch_site}'
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')]
)
def get_scatter_chart(launch_site, payload):
    df = spacex_df.loc[spacex_df['Payload Mass (kg)'].between(float(payload[0]), float(payload[1])), ['Launch Site', 'Payload Mass (kg)', 'class']]

    if launch_site == 'ALL':
        fig = px.scatter(
            data_frame=df,
            x='Payload Mass (kg)',
            y='class',
            title='Success launches to payload mass'
        )
        return fig
    else:
        fig = px.scatter(
            data_frame=df[df['Launch Site']==launch_site],
            x='Payload Mass (kg)',
            y='class',
            title=f'Success launches to payload mass for {launch_site}'
        )
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
