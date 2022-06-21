###############################
# Dash-app
# temperaturanomali fra toboksmodell
# fokus på strålingspådriv
# SDG613 - UiB
#
# juni 2022
# Bjarte Ursin
# bjarte.ursin@vlfk.no
#############################
import pandas as pd
import numpy as np
import plotly.express as px
import os.path
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template  # Bruker bootstap-template i plotly grafene

df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data','historical_IPCC6.csv'),
                 index_col=0, sep=',', encoding="utf-8")

df['total'] = df.sum(axis=1)

Template = 'flatly'  # bruk samme "theme" som under, men med småbokstaver
app = Dash(__name__,
           server=False,
           title='Toboksmodell og strålingspådriv',
           external_stylesheets=[dbc.themes.FLATLY],
           meta_tags=[{'name': 'viewport',  # skalering for mobil
                       'content': 'width=device-width, initial-scale=1.0'}])
load_figure_template(Template)

# ---------------------------------------------------------------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1(app.title,
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
                        ], xl=2, lg=4, md=12),
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
                        ], xl=6, lg=8, md=12),
                        dbc.Col([
                            dbc.InputGroup(
                                [dbc.InputGroupText('Enkeltpådriv'),
                                 dbc.InputGroupText(dbc.Switch(id='check_Sum', value=False)),
                                 dbc.InputGroupText("Sum av pådriv"),
                                 ],
                            )
                        ], align="end"),
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


# Strålingspådrivgraf henter
@app.callback(
    Output(component_id='small-graph', component_property='figure'),
    [Input(component_id='my_checklist', component_property='value'),
     Input(component_id='check_Sum', component_property='value')],
)
# ---------------------------------------------------------------------
# Callbacks
#
def update_graph(paadriv, check_Sum):
    dff = df[paadriv]
    sum_paadriv = dff.sum(axis=1).to_numpy()
    if check_Sum:
        fig = px.line(x=dff.index, y=sum_paadriv, title='Summen av strålingspådrivene', template=Template)
        fig.update_xaxes(title=dict(text='År'))
    else:
        fig = px.line(data_frame=dff, title='Strålingspådriv', template=Template)  # template='ggplot2'

    fig.update_traces(mode='lines')
    fig.update_yaxes(title=dict(text=r'$W / m^2$'))  # ,showgrid=True, gridwidth=1, gridcolor='white')
    fig.update_layout(legend=dict(
        orientation="h",
        # yanchor="bottom",
        y=1.15,
        xanchor="center",
        x=0.5,
        title=""
    ))

    return fig


@app.callback(
    Output(component_id='my-graph', component_property='figure'),
    Input(component_id='my_checklist', component_property='value'),
    prevent_initial_call=False
)
def tegn_temp_graf(driv, my_lambda=-1.3, my_gamma=-0.69):
    aar = df.index.tolist()
    lambda_sum = float(my_lambda)
    gamma = float(my_gamma)

    if len(driv) == 0:
        null = np.zeros(len(aar))
        fig3 = px.line(x=aar, y=null,
                       title='Velg strålingspådriv, sett andre parametre og trykk på knappen for å kjøre modell',
                       template=Template)
        fig3.update_layout(showlegend=False)
    else:

        radiative_forcing = df[driv].sum(axis=1).to_numpy()
        Ts, To = calculate_temp_anomalies(radiative_forcing, lambda_sum,
                                          gamma)  # kaller opp funksjonen som regner ut temperaturendringene
        temp = pd.DataFrame(index=df.index)  # vi lager en ny dataramme som har samme indexer (i.e. årstal) som pådrivet
        temp['Overflate'] = Ts
        temp['Dyphavet'] = To

        fig3 = px.line(data_frame=temp, template=Template)
        fig3.update_traces(mode='lines')
        fig3.update_yaxes(title=dict(text=r'$\Delta T [^{\circ} C]$'))
        fig3.update_layout(legend=dict(
            orientation="h",
            # yanchor="bottom",
            y=1.15,
            xanchor="center",
            x=0.5,
            title="Temperturanomali i havet for:"
        ))
    return fig3


if __name__ == '__main__':
    app.run_server(debug=True, port=83)
