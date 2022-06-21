###############################
# Dash-app
# temperaturanomali fra toboksmodell
# fokus på tilbakekoblingsmekanismer
# SDG613 - UiB
#
# juni 2022
# Bjarte Ursin
# bjarte.ursin@vlfk.no
##########################
import numpy as np
import plotly.express as px
import pandas as pd
import os.path
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template  # Bruker bootstap-template i plotly grafene

df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data",'historical_IPCC6.csv'), index_col=0, sep=',', encoding="utf-8")

df['total'] = df.sum(axis=1)

Template = 'flatly'  # bruk samme "theme" som under, men med småbokstaver
app = Dash(__name__,
           server=False,
           title='Tilbakekoblingsmekanismer',
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
                            dbc.InputGroup(
                                #                  [dbc.InputGroupText(dbc.Checkbox(id='check_Planck',value=True)),dbc.InputGroupText("Planck"),
                                [dbc.InputGroupText("Planck"),
                                 dbc.Input(id='my_Planck', type='text', value='-3.22')],
                            )
                        ], lg=3, md=6, align="end"),

                        dbc.Col([
                            dbc.InputGroup(
                                [dbc.InputGroupText(dbc.Checkbox(id='check_Laps', value=True)),
                                 dbc.InputGroupText("Lapse rate"),
                                 dbc.Input(id='my_Laps', type='text', value='-0.5')],
                            )
                        ], lg=3, md=6, align="end"),

                        dbc.Col([
                            dbc.InputGroup(
                                [dbc.InputGroupText(dbc.Checkbox(id='check_Water', value=True)),
                                 dbc.InputGroupText("Vanndamp"),
                                 dbc.Input(id='my_Water', type='text', value='1.77')],
                            )
                        ], lg=3, md=6, align="end"),

                        dbc.Col([
                            dbc.InputGroup(
                                [dbc.InputGroupText(dbc.Checkbox(id='check_Albedo', value=True)),
                                 dbc.InputGroupText("Albedo"),
                                 dbc.Input(id='my_Albedo', type='text', value='0.35')],
                            )
                        ], lg=3, md=6, align="end"),

                        dbc.Col([
                            dbc.InputGroup(
                                [dbc.InputGroupText(dbc.Checkbox(id='check_Clouds', value=True)),
                                 dbc.InputGroupText("Skyer"),
                                 dbc.Input(id='my_Clouds', type='text', value='0.42')],
                            )
                        ], lg=3, md=6, align="end"),

                        dbc.Col([
                            dbc.InputGroup([dbc.InputGroupText(dbc.Checkbox(id='check_Gamma', value=True)),
                                            dbc.InputGroupText("Gamma"),
                                            dbc.Input(id='my_Gamma', type='text', value='-0.69')],
                                           )
                        ], lg=3, md=6, align="end"),
                        dbc.Col([
                            dbc.InputGroup(
                                [dbc.InputGroupText('nullnivå: 1750'),
                                 dbc.InputGroupText(dbc.Switch(id='check_Null', value=False)),
                                 dbc.InputGroupText("1986-2005"),
                                 ],
                            )
                        ],), # width={"offset": 3}, align="end"),

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
    ]),
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
    ])
])


# _________________________________________________________________________________________________________
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


@app.callback(
    Output(component_id='my-graph', component_property='figure'),
    #     [Input(component_id='modell_knapp', component_property='n_clicks')],
    [Input(component_id='my_checklist', component_property='value'),
     Input(component_id='check_Laps', component_property='value'),
     Input(component_id='check_Water', component_property='value'),
     Input(component_id='check_Albedo', component_property='value'),
     Input(component_id='check_Clouds', component_property='value'),
     Input(component_id='check_Gamma', component_property='value'),
     Input(component_id='my_Planck', component_property='value'),
     Input(component_id='my_Laps', component_property='value'),
     Input(component_id='my_Water', component_property='value'),
     Input(component_id='my_Albedo', component_property='value'),
     Input(component_id='my_Clouds', component_property='value'),
     Input(component_id='my_Gamma', component_property='value'),
     Input(component_id='check_Null', component_property='value')
     ],
    prevent_initial_call=False
)
def tegn_temp_graf(driv, check_Laps, check_Water, check_Albedo, check_Clouds, check_Gamma,
                   my_Planck, my_Laps, my_Water, my_Albedo, my_Clouds, my_Gamma, check_Null):
    aar = df.index.tolist()
    lambda_sum = float(my_Planck)
    gamma = 0

    if check_Laps:
        lambda_sum += float(my_Laps)

    if check_Water:
        lambda_sum += float(my_Water)

    if check_Albedo:
        lambda_sum += float(my_Albedo)

    if check_Clouds:
        lambda_sum += float(my_Clouds)

    if check_Gamma:
        gamma = float(my_Gamma)

    # print(lambda_sum)

    if len(driv) == 0:
        null = np.zeros(len(aar))
        fig3 = px.line(x=aar, y=null, title='Velg minst ett strålingspådriv for å kjøre modell', template=Template)
        fig3.update_layout(showlegend=False)
    else:

        radiative_forcing = df[driv].sum(axis=1).to_numpy()
        Ts, To = calculate_temp_anomalies(radiative_forcing, lambda_sum,
                                          gamma)  # kaller opp funksjonen som regner ut temperaturendringene
        temp = pd.DataFrame(index=df.index)  # vi lager en ny dataramme som har samme indexer (i.e. årstal) som pådrivet
        temp['Overflate'] = Ts
        temp['Dyphavet'] = To

        if check_Null:
            temp['Overflate'] = temp['Overflate'] - temp['Overflate'].loc[1986:2005].mean()
            temp['Dyphavet'] = temp['Dyphavet'] - temp['Dyphavet'].loc[1986:2005].mean()

        fig3 = px.line(data_frame=temp, template=Template)
        fig3.update_traces(mode='lines')
        fig3.update_yaxes(title=dict(text=r'$\Delta T [^{\circ} C]$'))
        fig3.update_layout(
            height=400,
            legend=dict(
            orientation="h",
            # yanchor="bottom",
            y=1.15,
            xanchor="center",
            x=0.5,
            title="Temperturanomali i havet for:"
        ))
    return fig3


if __name__ == '__main__':
    app.run_server(debug=True, port=84)
