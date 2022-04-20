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

graph_section = html.Div([
    dbc.Row(
        [
            dbc.Col(
                dbc.Button(
                    "Generate Example", id='graph_button', n_clicks=0,
                    color='info',
                    style={'marginLeft': '2.5%', 'fontSize': 'large'}
                ),
                width='auto'
            ),
            dbc.Col(
                dbc.FormGroup(
                    [
                        dbc.Checkbox(
                            id='show_whites', className='form-check-input'
                        ),
                        dbc.Label(
                            'Show white damage', html_for='show_whites',
                            className='form-check-label'
                        )
                    ],
                    check=True
                ),
                width='auto'
            )
        ]
    ),
    html.H4(
        'Example of energy flow in a fight', style={'textAlign': 'center'}
    ),
    dcc.Graph(id='energy_flow'),
    html.Br(),
    dbc.Col(
        [
            html.H5('Combat Log'),
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th('Time'), html.Th('Event'), html.Th('Outcome'),
                    html.Th('Energy'), html.Th('Combo Points'), html.Th('Mana')
                ])),
                html.Tbody(id='combat_log')
            ])
        ],
        width=5, xl=4, style={'marginLeft': '2.5%'}
    )
])
