###############################
#Dash-app
#Energibalanse på jorden uten atmosfære
#SDG613 - UiB
#
#juni 2022
#Bjarte Ursin
#bjarte.ursin@vlfk.no
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
           title='Model uten atmoafære',
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
        ], width=12)  # ,style={'font-size': '2.5vw'})
    ], justify='center'),

    dbc.Row([
        dbc.Card([
            dbc.CardBody([
                html.H4("Balanser energien som stråler inn og ut fra jorden ved å regulere gjennomsnittstemperaturen",
                        className="card-title"),  # style={'font-size': '1.5vw'}),
                dbc.Row([dbc.Col(
                    dbc.Label("Temperatur målt i celsius"), lg=2, md=12),  # ,style={'font-size': '.95vw'}),

                    dbc.Col(dcc.Slider(-50, 50, .01, value=-30, marks=None, id='temp_slide',
                                       tooltip={"placement": "bottom", "always_visible": True}),
                            )
                ]),

                dbc.Row([
                    dbc.Col(
                        dbc.Label("Albedo:"), lg=2, md=12),  # ,style={'font-size': '.95vw'}),
                    dbc.Col(dcc.Slider(0, 1, .01, value=0.306, marks=None, id='alfa_slide',
                                       tooltip={"placement": "bottom", "always_visible": True}),
                            )
                ])
            ])
        ], color="primary", inverse=True)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='intensistet_graf', figure={}, mathjax=True)
            # , className='four columns')#,config={'staticPlot': True})
        ], lg=5, md=12, sm=12, xs=12, class_name="mt-3"),

        dbc.Col([
            dcc.Graph(id='pil_graf', figure={}, mathjax=True)
            # , className='four columns')#,config={'staticPlot': True})
        ], lg=7, md=12, sm=12, xs=12, class_name="mt-3")
    ])

],fluid='lg')


# _________________________________________________________________________________________________________

# #Pilfigur
@app.callback(
    Output(component_id='pil_graf', component_property='figure'),
    Input(component_id='temp_slide', component_property='value'),
    Input(component_id='alfa_slide', component_property='value')
)
def piler(temp, alfa):
    U = sigma * (temp + 273) ** 4
    skala = (4 * U / I_sol) * tyk

    fig = px.line(x=[0], y=[0])

    fig.add_annotation(ax=0.7, axref='x', ay=1.8, ayref='y',
                       x=0.7, xref='x', y=0.68, yref='y',
                       arrowwidth=tyk, arrowhead=7, arrowsize=0.3, text="Solinstråling", arrowcolor="gold",
                       arrowside='none')

    if tyk * (1 - alfa) > 0.1:
        fig.add_annotation(ax=0.7 + alfa * 0.025, axref='x', ay=0.9, ayref='y',
                           x=0.7 + alfa * 0.025, xref='x', y=0.2, yref='y',
                           arrowwidth=tyk * (1 - alfa), startarrowhead=6, arrowhead=4, arrowsize=0.3, arrowcolor="gold")

    if alfa * tyk > 0.1:
        fig.add_annotation(ax=0.5, axref='x', ay=1.78, ayref='y',
                           x=0.71, xref='x', y=0.54, yref='y', arrowside='start',
                           arrowwidth=alfa * tyk, arrowhead=6, startarrowhead=4, startarrowsize=0.3,
                           text="Reflektert sollys", arrowcolor="gold", align='left')

    if skala > 0.1:
        fig.add_annotation(ax=1, axref='x', ay=1.7, ayref='y',
                           x=1, xref='x', y=0.2, yref='y', arrowside='start',
                           arrowwidth=skala, startarrowhead=4, startarrowsize=0.3, text="Varmestråling",
                           arrowcolor="red", )

    fig.update_layout(xaxis_range=[0.3, 1.2], yaxis_range=[0, 2], margin_l=0, margin_r=0)

    fig.add_hrect(y0=0, y1=0.2, fillcolor="darkolivegreen", opacity=0.5, layer="below", line_width=0)
    fig.update_yaxes(showgrid=False, title=None, showticklabels=False)
    fig.update_xaxes(showgrid=False, title=None, showticklabels=False)
    return fig


@app.callback(
    Output(component_id='intensistet_graf', component_property='figure'),
    Input(component_id='temp_slide', component_property='value'),
    Input(component_id='alfa_slide', component_property='value')
)
def soyle(temp, alfa):
    U_jord = sigma * (temp + 273) ** 4
    I_max = I_sol / 4
    I_abs = I_max * (1 - alfa)

    grenser = [-8, I_abs - U_jord, I_max]  # for å bestemme ymax og ymin til skalering

    fig2 = px.line(x=[0], y=[0])

    # bakken
    fig2.add_shape(type="rect", x0=0, y0=I_abs, x1=1, y1=I_max,
                   line=dict(color="snow", width=2, ), fillcolor="lightgrey")

    fig2.add_shape(type="rect", x0=0, y0=0, x1=1, y1=I_abs,
                   line=dict(color="orange", width=2, ), fillcolor="gold")

    fig2.add_shape(type="rect", x0=1.5, y0=I_abs, x1=2.5, y1=I_abs - U_jord,
                   line=dict(color="Maroon", width=2, ), fillcolor="Red")

    fig2.add_shape(type="rect", x0=3, y0=0, x1=4, y1=I_abs - U_jord,
                   line=dict(color="RoyalBlue", width=2, ), fillcolor="LightSkyBlue")

    # tekst
    fig2.add_annotation(
        text="Energibalanse",
        xref="paper", yref="paper",
        x=0.51, y=1,
        showarrow=False,
        font=dict(size=16),
    )

    fig2.add_annotation(
        text="Inn",
        x=0.5, y=20,
        showarrow=False, textangle=0,
        font=dict(size=16),
    )

    fig2.add_annotation(
        text="Ut",
        x=2, y=20,
        showarrow=False, textangle=0,
        font=dict(size=16),
    )

    fig2.add_annotation(
        text="Bal.",
        x=3.5, y=20,
        showarrow=False, textangle=0,
        font=dict(size=16),
    )

    fig2.update_yaxes(title=dict(text=r'$W / m^2$'))
    fig2.update_xaxes(title=dict(text=r''))
    fig2.update_layout(title='', xaxis_range=[-0.3, 4.5], yaxis_range=[1.2 * min(grenser), 1.15 * max(grenser)],
                       legend=dict(orientation="h", y=1.15, xanchor="center", x=0.5,
                                   title=""))  # , yaxis_range = [0, 2],margin_l=0,margin_r=0)
    fig2.update_xaxes(showgrid=False, title=None, showticklabels=False)

    return fig2


if __name__ == '__main__':
    app.run_server(debug=True, port=88)
    # app.run_server(mode='inline')
