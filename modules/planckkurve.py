###############################
#Dash-app som tegner planckkurve
#SDG613 - UiB
#
#juni 2022
#Bjarte Ursin
#bjarte.ursin@vlfk.no
#############################
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template  # Bruker bootstap-template i plotly grafene


Template = 'flatly'  # bruk samme "theme" som under, men med småbokstaver
app = Dash(__name__,
           server=False,
           title='Planck - kurve',
           external_stylesheets=[dbc.themes.FLATLY],
           meta_tags=[{'name': 'viewport',  # skalering for mobil
                       'content': 'width=device-width, initial-scale=1.0'}])

load_figure_template(Template)
# --------------
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
                            dbc.Label(['Velg temperatur:']),
                        ], className="col-md-2"),
                        dbc.Col([
                            dcc.Slider(0, 6000, 1, value=14, marks=None,
                                       id='slider',
                                       tooltip={"placement": "top",
                                                "always_visible": True})
                        ], className="col-md-8")
                    ]),

                    dbc.Row([
                        dbc.Col([
                            dbc.Checklist(
                                id='my_dropdown',
                                options=[{'label': 'Låst y-akse', 'value': 'lock'},
                                         {'label': 'Logaritmisk y-akse', 'value': 'LGY'},
                                         {'label': 'Logaritmisk x-akse', 'value': 'LGX'},
                                         {'label': 'Regnbue', 'value': 'VIS'},
                                         {'label': 'Rutenett', 'value': 'GRID'}
                                         ],
                                value=['LGX', 'LGY', 'lock', 'VIS'],
                                inline=True)]
                        )
                    ])
                ])
            ], color="primary", inverse=True, class_name="mb-3")
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='my-graph', figure={}, mathjax=True,
                      )])
    ])
],fluid='lg')


# ---------------------------------------------

# konstanter
h = 6.62607015e-34  # Js - plancskonstant
c = 299792458  # m/s - Lysfarten i vakuum
k = 1.380649e-23  # J/K - Boltzmannkonstanten

# Bølgelender mellom 110nm til 100 mikrometer, jevnt fordelt på en logaritmiskskala.
lamda = np.logspace(np.log10(1.1e-7), np.log10(5e-5), num=1000, endpoint=True)


def u_planck(lamda, T):
    # Regner utstrålingstettheten ved hver bølgelengde for en gitt temperatur
    return (8 * np.pi * h * c) / (lamda ** 5) * (1 / (np.exp((h * c) / (lamda * k * T)) - 1))

@app.callback(
    Output(component_id='my-graph', component_property='figure'),
    Input(component_id='slider', component_property='value'),
    Input(component_id='my_dropdown', component_property='value'),
)
def plot(Temp, valg):
    T = Temp + 273
    U = u_planck(lamda, T)

    if 'LGX' in valg:
        LGX = True
    else:
        LGX = False

    if 'LGY' in valg:
        LGY = True
        ymin = -2
        ymax = 6.5
    else:
        LGY = False
        ymin = 0.01
        ymax = 1.6E6

    fig = px.line(x=lamda, y=U, log_y=LGY, log_x=LGX)

    fig.update_layout(
        xaxis_title='Bølgelengde (m)',
        yaxis_title='$W\cdot m^{-2}\cdot nm^{-1}$',
        height=550
    )
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True)
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True)

    if 'lock' in valg:  # løser y-aksen
        fig.update_layout(yaxis_range=[ymin, ymax])

    if 'VIS' in valg:  # viser regnbue
        fig.add_vrect(x0=440E-9, x1=460E-9, line_width=0, fillcolor='#8b00ff', layer='below')
        fig.add_vrect(x0=460E-9, x1=495E-9, line_width=0, fillcolor='#0000ff', layer='below')
        fig.add_vrect(x0=495E-9, x1=570E-9, line_width=0, fillcolor='#00ff00', layer='below')
        fig.add_vrect(x0=570E-9, x1=590E-9, line_width=0, fillcolor='#ffff00', layer='below')
        fig.add_vrect(x0=590E-9, x1=620E-9, line_width=0, fillcolor='#ff7f00', layer='below')
        fig.add_vrect(x0=620E-9, x1=750E-9, line_width=0, fillcolor='#ff0000', layer='below')

    if not 'GRID' in valg:  # slår av rutenett
        fig.update_layout(
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
