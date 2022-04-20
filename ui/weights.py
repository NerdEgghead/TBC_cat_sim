import dash
import pandas as pd
from dash import dash_table, dcc, html
import plotly.graph_objects as go
import numpy as np
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import tbc_cat_sim as ccs
import multiprocessing
import trinkets
import copy
import json
import base64
import io

weights_section = dbc.Col([
    html.H4('Stat Weights'),
    html.Div([
        dbc.Row(
            [
                dbc.Col(dbc.Button(
                    'Calculate Weights', id='weight_button', n_clicks=0,
                    color='info'
                ), width='auto'),
                dbc.Col(
                    [
                        dbc.FormGroup(
                            [
                                dbc.Checkbox(
                                    id='calc_mana_weights',
                                    className='form-check-input', checked=False
                                ),
                                dbc.Label(
                                    'Include mana weights',
                                    html_for='calc_mana_weights',
                                    className='form-check-label'
                                )
                            ],
                            check=True
                        ),
                        dbc.FormGroup(
                            [
                                dbc.Checkbox(
                                    id='epic_gems',
                                    className='form-check-input', checked=True
                                ),
                                dbc.Label(
                                    'Assume Epic gems',
                                    html_for='epic_gems',
                                    className='form-check-label'
                                )
                            ],
                            check=True
                        ),
                    ],
                    width='auto'
                )
            ]
        ),
        html.Div(
            'Calculation will take several minutes.',
            style={'fontWeight': 'bold'},
        ),
        dcc.Loading(
            children=[
                html.P(
                    children=[
                        html.Strong(
                            'Error: ', style={'fontSize': 'large'},
                            id='error_str'
                        ),
                        html.Span(
                            'Stat weight calculation requires the simulation '
                            'to be run with at least 20,000 replicates.',
                            style={'fontSize': 'large'}, id='error_msg'
                        )
                    ],
                    style={'marginTop': '4%'},
                ),
                dbc.Table([
                    html.Thead(html.Tr([
                        html.Th('Stat Increment'), html.Th('DPS Added'),
                        html.Th('Normalized Weight')
                    ])),
                    html.Tbody(id='stat_weight_table'),
                ]),
                html.Div(
                    html.A(
                        'Seventy Upgrades Import Link',
                        href='https://seventyupgrades.com', target='_blank'
                    ),
                    id='import_link'
                )
            ],
            id='loading_4', type='default'
        ),
    ]),
], style={'marginLeft': '5%', 'marginBottom': '2.5%'}, width=4, xl=3)
