###############################
#Dash-app som tegner
#oppvarming- og nedkjølingskurve
#
#Albedoforsøk
#SDG613 - UiB
#
#juni 2022
#Bjarte Ursin
#bjarte.ursin@vlfk.no
#############################

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template  # Bruker bootstap-template i plotly grafene

Albedo_med = pd.read_csv('data/Albedo_med_filter.csv', sep=';', decimal=',', index_col=0)
Albedo_uten = pd.read_csv('data/Albedo_uten_filter.csv', sep=';', decimal=',', index_col=0)

Template = 'flatly'  # bruk samme "theme" som under, men med småbokstaver
app = Dash(__name__,
           server=False,
           external_stylesheets=[dbc.themes.FLATLY],
           meta_tags=[{'name': 'viewport',  # skalering for mobil
                       'content': 'width=device-width, initial-scale=1.0'}])

load_figure_template(Template)
# --------------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Albedoeksperiment',
                    className='text-center text-primary mb-4')
        ], width=12)
    ], justify='center'),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label(['Velg forsøk:']),
                        ], className="col-md-2"),
                        dbc.Col([
                            dbc.Checklist(
                                id='my_checklist',
                                options=[
                                    {'label': 'Uten filter', 'value': 'uten'},
                                    {'label': 'Med filter', 'value': 'med'},
                                ],
                                value=['uten'],
                                inline=True)  # ,width=8)
                        ], className="col-md-8")
                    ])
                ])
            ], color="primary", inverse=True, class_name="mb-3")
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='my-graph', figure={},
                      mathjax=True,
                      )])
    ])
],fluid='lg')


# ---------------------------------------------
@app.callback(
    Output(component_id='my-graph', component_property='figure'),
    Input(component_id='my_checklist', component_property='value')
)
def plot(valg):
    fig = go.Figure()

    if 'uten' in valg:
        fig.add_trace(go.Scatter(x=Albedo_uten.index, y=Albedo_uten.iloc[:, 0],
                                 name='Blank - uten filter', line=dict(color='gray')))
        fig.add_trace(go.Scatter(x=Albedo_uten.index, y=Albedo_uten.iloc[:, 1],
                                 name='Svart - uten filter', line=dict(color='black')))
    if 'med' in valg:
        fig.add_trace(go.Scatter(x=Albedo_med.index, y=Albedo_med.iloc[:, 0],
                                 name='Blank - med filter', line=dict(color='gray', dash='dash')))
        fig.add_trace(go.Scatter(x=Albedo_med.index, y=Albedo_med.iloc[:, 1],
                                 name='Svart - med filter ', line=dict(color='black', dash='dash')))

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99
    ),
        #                title='Albedoforsøk',
        xaxis_title='Tid (min)',
        yaxis_title='Temperatur (' + '\u2103' + ')',
        #                title_font_size=30
        yaxis_range=[21, 37],
        xaxis_range=[0, 17]
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=82)
