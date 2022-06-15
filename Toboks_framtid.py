###############################
# Dash-app
# temperaturanomali fra toboksmodell
# fokus på fremtidsscenarier
# SDG613 - UiB
#
# juni 2022
# Bjarte Ursin
# bjarte.ursin@vlfk.no
##########################
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template  # Bruker bootstap-template i plotly grafene


df = pd.read_csv('Data/futureForcing_IPCC6.csv',
                 index_col=0, sep=',', encoding="utf-8")

Template = 'flatly'  # bruk samme "theme" som under, men med småbokstaver
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
           meta_tags=[{'name': 'viewport',  # skalering for mobil
                       'content': 'width=device-width, initial-scale=1.0'}])

load_figure_template(Template)
# ---------------------------------------------------------------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Toboksmodell og fremtidsscenarier',
                    className='text-center text-primary mb-4')
        ], width=12)
    ], justify='center'),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label(['Velg utviklingsbane:']),
                        ], xl=2, lg=4, md=12),
                        dbc.Col([
                            dbc.Checklist(
                                id='my_checklist',
                                options=[
                                    {'label': 'SSP1', 'value': 'SSP1-2.6'},
                                    {'label': 'SSP2?', 'value': 'SSP2', "disabled": True},
                                    {'label': 'SSP3?', 'value': 'SSP3', "disabled": True},
                                    {'label': 'SSP4?', 'value': 'SSP4', "disabled": True},
                                    {'label': 'SSP5', 'value': 'SSP5-8.5'},
                                ],
                                value=['SSP1-2.6'],  # hukker alle av til å begynne med.
                                inline=True)  # ,width=8)
                        ], xl=4, lg=8, md=12),

                        dbc.Col([
                            dbc.Label(['Andre valg:']),
                        ], xl=1, lg=4, md=12),
                        dbc.Col([
                            dbc.Checklist(
                                id='my_checklist2',
                                options=[
                                    {'label': 'Dyphav', 'value': 'hav'},
                                    {'label': 'Nullnivå 1986-2005', 'value': '1986:2005'},
                                    {'label': 'Usikkerhet i lambda', 'value': 'lambda'},
                                ],
                                value=['hav'],
                                inline=True)  # ,width=8)
                        ], xl=5, lg=8, md=12),

                    ])
                ])
            ], color="primary", inverse=True, class_name="mb-3")
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='small-graph', figure={}, mathjax=True)
            # , className='four columns')#,config={'staticPlot': True})
        ], width=4),

        dbc.Col([
            dcc.Graph(id='my-graph', figure={},
                      mathjax=True,
                      )], width=8)
    ]),
    dbc.Row([
        dbc.Card([
            dbc.CardBody([
                html.H4("Velg perioder for plottet:", className="card-title"),
                dbc.Row([

                    dbc.Col(dcc.RangeSlider(1750, 2500,
                                            marks={
                                                1750: '1750',
                                                1800: '1800',
                                                1850: '1850',
                                                1900: '1900',
                                                1950: '1950',
                                                2000: '2000',
                                                2050: '2050',
                                                2100: '2100',
                                                2200: '2200',
                                                2300: '2300',
                                                2400: '2400',
                                            },
                                            value=[1850, 2100],
                                            id='slide1'),
                            )
                ]),
            ])
        ], color="primary", inverse=True)
    ])
], fluid='lg')


# _________________________________________________________________________________________________________
#
def calculate_temp_anomalies(radiative_forcing, lambda_sum, gamma):
    H_MIX = 100  # tykkelse av blandingslaget [m]
    H_DEEP = 3700 - H_MIX  # gjennomsnitts tykkelse av dyphavet [m]
    RHO = 1000  # vannets tetthet (kg m-3)
    CPO = 4200  # spesifikk varmekapasitet for vann(J kg-1 K-1)
    f_o = 0.7  # andel av jordens overflate dekket av vann

    Dt = 365 * 24 * 60 * 60  # steglenge i modellen - 1 år i sekund

    # effektiv varmekapasitet for atmosfære-hav-systemet [J m-2 K-1]
    # Hvor mye energi skal til for å heve en vannsøyle med grunnflate en kvadratmeter og høyde
    # tilsvarende havdybden en grad.

    CEFF_M = f_o * H_MIX * CPO * RHO
    CEFF_D = f_o * H_DEEP * CPO * RHO

    Ts = np.array([0])  # Starter temperaturseriene med temperaturen første år.
    To = np.array([0])

    for t in range(1, len(radiative_forcing)):
        # --------------
        # Temperatur tendenser (den deriverte) [K/s]
        #     dTs/dt, dTo/dt
        # --------------
        dTs_dt = (radiative_forcing[t] + (lambda_sum * Ts[t - 1]) + (gamma * (Ts[t - 1] - To[t - 1]))) / CEFF_M
        dTo_dt = -gamma * (Ts[t - 1] - To[t - 1]) / CEFF_D

        # ----------------------------------------------------------------------
        # Antar konstant temperaturendring i løpet av et år, regner ut ny temperatur
        # ved hjelp av Eulermetoden og oppdaterer temperaturarrayene
        # ----------------------------------------------------------------------
        Ts = np.append(Ts, Ts[t - 1] + dTs_dt * Dt)
        To = np.append(To, To[t - 1] + dTo_dt * Dt)
    return Ts, To


#
@app.callback(
    Output(component_id='small-graph', component_property='figure'),
    [Input(component_id='my_checklist', component_property='value'),
     Input(component_id='slide1', component_property='value')]
)
def update_graph(paadriv, periode):
    dff = df[paadriv]

    fig = px.line(data_frame=dff, title='Samlet strålingspådriv', template=Template)  # template='ggplot2'

    ymax = np.max(dff.loc[periode[0]:periode[1]].max())
    ymin = np.min(dff.loc[periode[0]:periode[1]].min())

    fig.update_traces(mode='lines')
    fig.update_yaxes(title=dict(text=r'$W / m^2$'))  # ,showgrid=True, gridwidth=1, gridcolor='white')
    fig.update_xaxes(title=dict(text='År'))
    fig.update_layout(legend=dict(
        # orientation="h",
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        title="Utviklingbaner"
    ),
        xaxis_range=[periode[0], periode[1]],
        yaxis_range=[ymin * 1.05, ymax * 1.05],
        height=500
    )

    return fig


lambda_planck = (-3.22, -3.4, -3.0, 'high')
lamdba_WV = (1.77, 1.57, 1.97, 'high')  # from Zelinka et al., 2020 (one standard deviation)
lamdba_LR = (-0.5, -0.7, -0.3, 'high')  # from Dessler, 2013; Caldwell et al., 2016; Colman and Hanson,
                                        # 2017; Zelinka et al., 2020 (one standard deviation)
lambda_albedo = (0.35, 0.1, 0.6, 'medium')
lambda_cloud = (0.42, -0.1, 0.94, 'high')

lambda_sum_min = lambda_planck[1] + lamdba_WV[1] + lamdba_LR[1] + lambda_albedo[1] + lambda_cloud[1]
lambda_sum_max = lambda_planck[2] + lamdba_WV[2] + lamdba_LR[2] + lambda_albedo[2] + lambda_cloud[2]

lambda_sum = lambda_planck[0] + lamdba_WV[0] + lamdba_LR[0] + lambda_albedo[0] + lambda_cloud[0]

sum_var = ((lambda_planck[1] - lambda_planck[0]) / 2) ** 2 + ((lamdba_WV[1] - lamdba_WV[0]) / 2) ** 2 + (
        (lamdba_LR[1] - lamdba_LR[0]) / 2) ** 2 + ((lambda_albedo[1] - lambda_albedo[0]) / 2) ** 2 + (
                  (lambda_cloud[1] - lambda_cloud[0]) / 2) ** 2
Std = sum_var ** 0.5


# lambda_sum_min=lambda_sum-Std
# lambda_sum_max=lambda_sum+Std

# Temperaturanomali
@app.callback(
    Output(component_id='my-graph', component_property='figure'),
    [Input(component_id='my_checklist', component_property='value'),
     Input(component_id='my_checklist2', component_property='value'),
     Input(component_id='slide1', component_property='value')],
)
def update_temperatur(paadriv, check, periode):
    dff = df[paadriv]
    nivaa1 = 1750
    nivaa2 = 1750

    if '1986:2005' in check:
        nivaa1 = 1986
        nivaa2 = 2005

    if 'hav' in check:
        gamma = -0.69
    else:
        gamma = 0

    temp = pd.DataFrame(index=dff.index)

    for i in range(len(paadriv)):
        temp[paadriv[i]], To = calculate_temp_anomalies(dff[paadriv[i]].to_numpy(), lambda_sum, gamma)
        temp[paadriv[i]] = temp[paadriv[i]] - temp[paadriv[i]].loc[nivaa1:nivaa2].mean()

    fig = px.line(data_frame=temp, title='Temperaturanomali overflate', template=Template)
    fig.update_yaxes(title=dict(text=r'$\Delta T [^{\circ} C]$'))
    fig.update_xaxes(title=dict(text='År'))

    ymax = np.max(temp.loc[periode[0]:periode[1]].max())
    ymin = np.min(temp.loc[periode[0]:periode[1]].min())

    if 'lambda' in check:
        min_temp = pd.DataFrame(index=dff.index)
        max_temp = pd.DataFrame(index=dff.index)

        for i in range(len(paadriv)):
            min_temp[paadriv[i]], To = calculate_temp_anomalies(dff[paadriv[i]].to_numpy(), lambda_sum_min, gamma)
            min_temp[paadriv[i]] = min_temp[paadriv[i]] - min_temp[paadriv[i]].loc[nivaa1:nivaa2].mean()

            max_temp[paadriv[i]], To = calculate_temp_anomalies(dff[paadriv[i]].to_numpy(), lambda_sum_max, gamma)
            max_temp[paadriv[i]] = max_temp[paadriv[i]] - max_temp[paadriv[i]].loc[nivaa1:nivaa2].mean()

            fig.add_trace(go.Scatter(x=max_temp.index, y=max_temp[paadriv[i]],
                                     fill='none',
                                     mode='lines',
                                     line_color=px.colors.qualitative.Plotly[i],
                                     showlegend=False,
                                     name='max',
                                     opacity=0.01
                                     ))

            fig.add_trace(go.Scatter(x=min_temp.index, y=min_temp[paadriv[i]],
                                     fill='tonexty',
                                     mode='lines',
                                     line_color=px.colors.qualitative.Plotly[i],
                                     name='min',
                                     showlegend=False,
                                     opacity=0.01
                                     ))

        ymax = np.max([max_temp.loc[periode[0]:periode[1]].max(), min_temp.loc[periode[0]:periode[1]].min()])
        ymin = np.min([max_temp.loc[periode[0]:periode[1]].max(), min_temp.loc[periode[0]:periode[1]].min()])

    fig.update_layout(legend=dict(
        # orientation="h",
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        title="Utviklingbaner"
    ),
        xaxis_range=[periode[0], periode[1]],
        yaxis_range=[ymin * 1.05, ymax * 1.05],
        height=500
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=60)
