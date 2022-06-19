###############################
# Dash-app
# Energibalanse - atmosfæren som et lag
# SDG613 - UiB
#
# juni 2022
# Bjarte Ursin
# bjarte.ursin@vlfk.no
#############################
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template  # Bruker bootstap-template i plotly grafene

sigma = 5.67E-8  # Stefan-Boltzmann konstant (W.m-2.K-4)
I_sol = 1361  #
tyk = 50  # 100% - piltykkelse

Template = 'flatly'  # bruk samme "theme" som under, men med småbokstaver

app = Dash(__name__,
           server=False,
           title='Ettlagsmodell av atmosfæren',
           external_stylesheets=[dbc.themes.FLATLY],
           meta_tags=[{'name': 'viewport',  # skalering for mobil
                       'content': 'width=device-width, initial-scale=0.9'}]
           )

load_figure_template(Template)

# ---------------------------------------------------------------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1(app.title,  # style={'font-size': '2.5vw'},
                    className='text-center text-primary mb-4')
        ], width=12)
    ], justify='center'),

    dbc.Row([
        dbc.Card([
            dbc.CardBody([
                html.H4(
                    "Balanser energien som stråler ut og inn:",
                    className="card-title"),  # style={'font-size': '1.2vw'}),
                dbc.Row([dbc.Col(
                    dbc.Label("Temperatur på bakken"), width=2),  # style={'font-size': '.95vw'}),

                    dbc.Col(dcc.Slider(-50, 50, .01, value=-30, marks=None, id='temp_slide',
                                       tooltip={"placement": "bottom", "always_visible": True}),
                            )
                ]),
                # ,width=3,align="end"),
                dbc.Row([
                    dbc.Col(
                        dbc.Label("Temperatur i atmosfæren:"), width=2),  # style={'font-size': '.95vw'}),
                    dbc.Col(dcc.Slider(-100, 10, .01, value=-50, marks=None, id='temp2_slide',
                                       tooltip={"placement": "bottom", "always_visible": True}),
                            )
                ])
            ])
        ], color="primary", inverse=True, class_name="mb-3")
    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(id='pil_graf', figure={}, mathjax=True)
            # , className='four columns')#,config={'staticPlot': True})
        ], lg=7, md=12, sm=12, xs=12, class_name="mb-3"),

        dbc.Col([
            dcc.Graph(id='intensistet_graf', figure={}, mathjax=True)
            # , className='four columns')#,config={'staticPlot': True})
        ], lg=5, md=12, sm=12, xs=12, class_name="mb-3", width={'order': 'last'})

    ]),

    dbc.Row([
        dbc.Card([
            dbc.CardBody([
#                html.H4(
#                    "Reguler andelen av solyset som reflekteres (albedo) og hvor effektiv atmosfæren absorberer og "
#                    "sender ut langbølget stråling (emissivitet)",
#                    # style={'font-size': '1.2vw'},
#                    className="card-title"),
                dbc.Row([dbc.Col(
                    dbc.Label("Albedo"), width=2),  # style={'font-size': '.95vw'}),

                    dbc.Col(dcc.Slider(0, 1, .01, value=0.306, marks=None, id='alfa_slide',
                                       tooltip={"placement": "bottom", "always_visible": True})
                            ),
                ]),
                dbc.Row([
                    dbc.Col(
                        dbc.Label("Emissivitet"), width=2),  # style={'font-size': '.95vw'}),
                    dbc.Col(dcc.Slider(0, 1, .01, value=0.77, marks=None, id='epsilon_slide',
                                       tooltip={"placement": "bottom", "always_visible": True})

                            )
                ])
            ])
        ], color="primary", inverse=True, class_name="mb-3")
    ])

],fluid='lg')


# _________________________________________________________________________________________________________

# #Pilfigur
@app.callback(
    Output(component_id='pil_graf', component_property='figure'),
    Input(component_id='temp_slide', component_property='value'),
    Input(component_id='temp2_slide', component_property='value'),
    Input(component_id='alfa_slide', component_property='value'),
    Input(component_id='epsilon_slide', component_property='value')
)
def piler(temp, temp2, alfa, epsilon):
    # epsilon=0.8
    U = sigma * (temp + 273) ** 4
    U_atm = epsilon * sigma * (temp2 + 273) ** 4
    skala = (4 * U / I_sol) * tyk
    skala2 = skala * (1 - epsilon)
    skala = skala * epsilon
    skala3 = (4 * U_atm / I_sol) * tyk

    fig = px.line(x=[0], y=[0])

    fig.add_annotation(ax=0.7, axref='x', ay=2.2, ayref='y',
                       x=0.7, xref='x', y=0.68, yref='y',
                       arrowwidth=tyk, arrowhead=7, arrowsize=0.3, text="Solinnstråling", arrowcolor="gold",
                       arrowside='none')

    if (1 - alfa) > 0.1:
        fig.add_annotation(ax=0.7 + alfa * 0.025, axref='x', ay=0.9, ayref='y',
                           x=0.7 + alfa * 0.025, xref='x', y=0.2, yref='y',
                           arrowwidth=tyk * (1 - alfa), startarrowhead=6, arrowhead=4, arrowsize=0.3, arrowcolor="gold")

    if alfa > 0.1:
        fig.add_annotation(ax=0.5, axref='x', ay=2.2, ayref='y',
                           x=0.69, xref='x', y=0.60, yref='y', arrowside='start',
                           arrowwidth=alfa * tyk, arrowhead=6, startarrowhead=4, startarrowsize=0.3,
                           text="Reflektert <br> sollys", arrowcolor="gold", align='left')

    if skala > 0.1:
        fig.add_annotation(ax=0.99, axref='x', ay=1.2, ayref='y',
                           x=0.99, xref='x', y=0.2, yref='y', arrowside='start',
                           arrowwidth=skala, startarrowhead=4, startarrowsize=0.3, arrowcolor="red",
                           text='Varmestråling<br>absorbet<br>i atm.')

    if skala2 > 0.1:
        fig.add_annotation(ax=1.12, axref='x', ay=2.2, ayref='y',
                           x=1.01, xref='x', y=0.2, yref='y', arrowside='start',
                           arrowwidth=skala2, startarrowhead=4, startarrowsize=0.3,
                           text="Varmeståling<br>mot verdens-<br>rommet", arrowcolor="red", )
    if skala3 > 0.1:
        fig.add_annotation(ax=1.35, axref='x', ay=2.2, ayref='y',
                           x=1.35, xref='x', y=0.2, yref='y', arrowside='end+start',
                           arrowwidth=skala3, arrowhead=4, startarrowhead=4, startarrowsize=0.3, arrowsize=0.3,
                           text="Atmosfæren<br>sender ut<br>varmestråling", arrowcolor="FireBrick", )

    fig.update_layout(xaxis_range=[0.4, 1.5],
                      yaxis_range=[0, 2],
                      margin_l=0,
                      margin_r=0,
                      height=400)

    fig.add_hrect(y0=0, y1=0.2, fillcolor="DarkOliveGreen", opacity=0.5, layer="below", line_width=0)
    fig.add_hrect(y0=1, y1=1.4, fillcolor="lightblue", opacity=0.5, layer="above", line_width=0)
    fig.update_yaxes(showgrid=False, title=None, showticklabels=False)
    fig.update_xaxes(showgrid=False, title=None, showticklabels=False)
    return fig


@app.callback(
    Output(component_id='intensistet_graf', component_property='figure'),
    Input(component_id='temp_slide', component_property='value'),
    Input(component_id='temp2_slide', component_property='value'),
    Input(component_id='alfa_slide', component_property='value'),
    Input(component_id='epsilon_slide', component_property='value')
)
def soyle(temp, temp2, alfa, epsilon):
    U_jord = sigma * (temp + 273) ** 4
    I_max = I_sol / 4
    I_abs = I_max * (1 - alfa)
    U_atm = epsilon * sigma * (temp2 + 273) ** 4
    grenser = [-8, I_abs + U_atm, I_abs + U_atm - U_jord,
               epsilon * U_jord - 2 * U_atm]  # for å bestemme ymax og ymin til skalering

    fig2 = px.line(x=[0], y=[0])

    # bakken
    fig2.add_shape(type="rect", x0=0, y0=I_abs, x1=1, y1=I_abs + U_atm,
                   line=dict(color="DarkRed", width=2, ), fillcolor="FireBrick")

    fig2.add_shape(type="rect", x0=0, y0=0, x1=1, y1=I_abs,
                   line=dict(color="orange", width=2, ), fillcolor="gold")

    fig2.add_shape(type="rect", x0=1.5, y0=I_abs + U_atm, x1=2.5, y1=I_abs + U_atm - U_jord,
                   line=dict(color="Maroon", width=2, ), fillcolor="Red")

    fig2.add_shape(type="rect", x0=3, y0=0, x1=4, y1=I_abs + U_atm - U_jord,
                   line=dict(color="RoyalBlue", width=2, ), fillcolor="LightSkyBlue")

    # atmosfæren
    fig2.add_shape(type="rect", x0=5.5, y0=0, x1=6.5, y1=epsilon * U_jord,
                   line=dict(color="Maroon", width=2, ), fillcolor="Red")

    fig2.add_shape(type="rect", x0=7, y0=epsilon * U_jord, x1=8, y1=epsilon * U_jord - 2 * U_atm,
                   line=dict(color="DarkRed", width=2, ), fillcolor="FireBrick")

    fig2.add_shape(type="rect", x0=8.5, y0=0, x1=9.5, y1=epsilon * U_jord - 2 * U_atm,
                   line=dict(color="RoyalBlue", width=2, ), fillcolor="LightSkyBlue")

    # tekst
    fig2.add_annotation(
        text="Energibalanse<br>jord",
        xref="paper", yref="paper",
        x=0.11, y=1,
        showarrow=False,
        font=dict(size=16),
    )

    fig2.add_annotation(
        text="Energibalanse<br>atmosfære",
        xref="paper", yref="paper",
        x=0.91, y=1,
        showarrow=False, textangle=0,
        font=dict(size=16),
    )

    fig2.add_annotation(
        text="Inn",
        x=0.5, y=40,
        showarrow=False, textangle=0,
        font=dict(size=16),
    )

    fig2.add_annotation(
        text="Ut",
        x=2, y=40,
        showarrow=False, textangle=0,
        font=dict(size=16),
    )

    fig2.add_annotation(
        text="Bal.",
        x=3.5, y=40,
        showarrow=False, textangle=0,
        font=dict(size=16),
    )

    fig2.add_annotation(
        text="Inn",
        x=6, y=40,
        showarrow=False, textangle=0,
        font=dict(size=16),
    )

    fig2.add_annotation(
        text="Ut",
        x=7.5, y=40,
        showarrow=False, textangle=0,
        font=dict(size=16),
    )

    fig2.add_annotation(
        text="Bal.",
        x=9, y=40,
        showarrow=False, textangle=0,
        font=dict(size=16),
    )

    fig2.add_hline(y=0)
    fig2.update_yaxes(title=dict(text=r'$W / m^2$'))
    fig2.update_xaxes(title=dict(text=r''))
    fig2.update_layout(title='',
                       xaxis_range=[-0.5, 10],
                       yaxis_range=[1.2 * min(grenser), 1.15 * max(grenser)],
                       legend=dict(orientation="h", y=1.15, xanchor="center", x=0.5, title=""),
                       height=400,
                       )
    fig2.update_xaxes(showgrid=False, title=None, showticklabels=False)

    return fig2


if __name__ == '__main__':
    app.run_server(debug=True, port=73)
