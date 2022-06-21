###############################
# Dash-app
# strålingspådriv til toboksmodell
#
# SDG613 - UiB
#
# juni 2022
# Bjarte Ursin
# bjarte.ursin@vlfk.no
##########################

import pandas as pd
import plotly.express as px
import os.path

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template  # Bruker bootstap-template i plotly grafene

# df=pd.read_csv('historical.csv',index_col = 0,sep=',',encoding = "utf-8")
df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", 'historical_IPCC6.csv'),
                 index_col=0, sep=',', encoding="utf-8")


df['total'] = df.sum(axis=1)

Template = 'flatly'  # bruk samme "theme" som under, men med småbokstaver
app = Dash(__name__,
           server=False,
           title='Historisk strålingspådriv',
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
                        ], className="col-md-2"),
                        dbc.Col({
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
                                inline=True),  # ,width=8)
                        }, className="col-md-8")
                    ])
                ])
            ], color="primary", inverse=True, class_name="mb-3")
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='pie-graph', figure={}, mathjax=True)
            # , className='four columns')#,config={'staticPlot': True})
        ], width=4),

        dbc.Col([
            dcc.Graph(id='my-graph', figure={},
                      mathjax=True,
                      )], width=8)
    ]),

    dbc.Col([
        dcc.Graph(id='total-graph', figure={},
                  mathjax=True,
                  )])  # ,width=8)
], fluid='lg')


# _________________________________________________________________________________________________________
#
# Strålingspådrivgraf henter
@app.callback(
    Output(component_id='my-graph', component_property='figure'),
    Input(component_id='my_checklist', component_property='value'),
)
def update_graph(paadriv):
    dff = df[paadriv]
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


# sektordiagram henter årstall fra "hoverdata"
@app.callback(
    Output(component_id='pie-graph', component_property='figure'),
    Input(component_id='my-graph', component_property='hoverData'),
    Input(component_id='my_checklist', component_property='value')
)
def update_side_graph(hov_data, paadriv):  # clk_data, slct_data, paadriv):
    if hov_data is None:
        dff2 = df[paadriv].loc[1952]
        # dff2 = np.abs(dff2.loc[ 1952.0])
        dff2 = dff2.to_frame(name='verdi')
        dff2.reset_index(inplace=True)
        fig2 = px.bar(dff2, x='index', y='verdi', color='index', title='Fordeling av strålingspådriv i 1952',
                      template=Template)

    else:
        hov_year = hov_data['points'][0]['x']
        dff2 = df[paadriv].loc[hov_year]
        # dff2 = np.abs(dff2.loc)
        dff2 = dff2.to_frame(name='verdi')
        dff2.reset_index(inplace=True)
        fig2 = px.bar(dff2, x='index', y='verdi', color='index', title=f'Fordeling av strålingspådriv i {hov_year}',
                      template=Template)

    fig2.update_layout(height=400,showlegend=False)
    fig2.update_yaxes(title=dict(text=r'$W / m^2$'))
    fig2.update_xaxes(title=dict(text=r''))

    return fig2


@app.callback(
    Output(component_id='total-graph', component_property='figure'),
    Input(component_id='my_checklist', component_property='value')
)
def update_total(paadriv):
    if len(paadriv) == 1:
        liste = ''.join(paadriv)
    else:
        liste = paadriv[:-1] + [' '.join(['og', paadriv[-1]])]
        liste = ', '.join(liste)
    fig3 = px.line(x=df.index, y=df[paadriv].sum(axis=1), title=f'Total strålingspådriv: {liste}', template=Template)
    fig3.update_yaxes(title=dict(text=r'$W / m^2$'))  # ,showgrid=True, gridwidth=1, gridcolor='white')
    fig3.update_layout(height=400, showlegend=False)
    fig3.update_xaxes(title='')
    return fig3


if __name__ == '__main__':
    app.run_server(debug=True, port=81)
