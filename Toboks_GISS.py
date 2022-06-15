###############################
# Dash-app
# temperaturanomali fra toboksmodell og GISS
# https://data.giss.nasa.gov/gistemp/graphs_v4/
# SDG613 - UiB
#
# juni 2022
# Bjarte Ursin
# bjarte.ursin@vlfk.no
#############################

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template  # Bruker bootstap-template i plotly grafene

# df=pd.read_csv('historical.csv',index_col = 0,sep=',',encoding = "utf-8")
df = pd.read_csv('Data/historical_IPCC6.csv',
                 index_col=0, sep=',', encoding="utf-8")

# df['total']=df.sum(axis=1)
data = pd.read_csv('Data/graph.csv', skiprows=1, index_col=0)
error = pd.read_csv('Data/totalCI_ERA.csv', index_col=0)
data['Max'] = data['No_Smoothing'] + error['ci95']
data['Min'] = data['No_Smoothing'] - error['ci95']

lambda_sum = -1.3  # [Wm-2K-1] - Parameter for tilbakekobling,sum av gjennomsnitt fra Soden and Held (2006)
gamma = -0.69  # [Wm-2K-1] - effektivitet for opptak av varme i dyphav fra Dufresne and Bony (2008)

Template = 'flatly'  # bruk samme "theme" som under, men med småbokstaver
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
           meta_tags=[{'name': 'viewport',  # skalering for mobil
                       'content': 'width=device-width, initial-scale=1.0'}])

load_figure_template(Template)
# ---------------------------------------------------------------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Målt + modelert temperaturanomali',
                    className='text-center text-primary mb-4')
        ], width=12)
    ], justify='center'),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label(['Velg strålingspådriv:']),
                        ], className="col-md-2"),
                        dbc.Col([
                            dbc.Checklist(
                                id='my_checklist',
                                options=[
                                    {'label': 'Drivhusgasser', 'value': 'drivhusgasser'},
                                    {'label': 'Solinnstråling', 'value': 'solinnstråling'},
                                    {'label': 'Vulkanisme', 'value': 'vulkanisme'},
                                    {'label': 'Arealbruk', 'value': 'arealbruk'},
                                    {'label': 'Aerosoler', 'value': 'aerosoler'},
                                ],
                                value=['drivhusgasser', 'solinnstråling', 'vulkanisme', 'arealbruk', 'aerosoler'],
                                # hukker alle av til å begynne med.
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
], fluid='lg')


# ---------------------------------------------
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


df1 = df.loc[1850:]
radiative_forcing = df1.sum(axis=1).to_numpy()
Temps, Tempo = calculate_temp_anomalies(radiative_forcing, lambda_sum, gamma)
referanseverdi = np.mean(Temps[101:131])


@app.callback(
    Output(component_id='my-graph', component_property='figure'),
    Input(component_id='my_checklist', component_property='value')
)
def tegn_sum_graf(driv):
    df1 = df.loc[1850:]
    radiative_forcing = df1[driv].sum(axis=1).to_numpy()
    Ts, To = calculate_temp_anomalies(radiative_forcing, lambda_sum,
                                      gamma)  # kaller opp funksjonen som regner ut temperaturendringene
    # Ts=Ts-np.mean(Ts[101:131])
    Ts = Ts - referanseverdi  # setter nullnivå 1951-80, med alle strålingspådriv
    temp = pd.DataFrame(
        index=df.loc[1850:].index)  # vi lager en ny dataramme som har samme indexer (i.e. årstal) som pådrivet
    temp['Temp.endring overflate'] = Ts
    # temp['Temp.endring dyphavet']=To

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=temp.index, y=temp['Temp.endring overflate'],
                             fill=None,
                             mode='lines',
                             line_color='black',
                             name='Toboks'
                             ))

    fig.add_trace(go.Scatter(x=data.index, y=data['No_Smoothing'],
                             fill=None,
                             mode='lines',
                             line_color='red',
                             name='GISS',
                             ))

    fig.add_trace(go.Scatter(x=data.index, y=data['Max'],
                             fill=None,
                             mode='lines',
                             line_color='gray',
                             showlegend=False,
                             name='Max'
                             ))

    fig.add_trace(go.Scatter(x=data.index, y=data['Min'],
                             fill='tonexty',
                             mode='lines',
                             line_color='gray',
                             name='min',
                             showlegend=False,
                             ))

    fig.update_yaxes(title=dict(text=r'$\Delta T [^{\circ} C]$'))

    fig.update_layout(yaxis_range=[-1.3, 1.6],
                      height=500)
    #     title="Plot Title",
    #     xaxis_title="X Axis Title",
    #     yaxis_title="Y Axis Title",
    #     legend_title="Legend Title",
    #     font=dict(
    #         family="Courier New, monospace",
    #         size=18,
    #         color="RebeccaPurple"
    #     )
    # )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=80)
