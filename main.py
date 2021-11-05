# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import numpy as np
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import tbc_cat_sim as ccs
import multiprocessing
import trinkets
import copy


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server


stat_input = dbc.Col([
    html.H5('Unbuffed Cat Form Stats'),
    html.Div([
        html.Div(
            'Strength:',
            style={
                'width': '40%', 'display': 'inline-block',
                'fontWeight': 'bold'
            }
        ),
        dbc.Input(
            type='number', value=336, id='unbuffed_strength',
            style={
                'width': '30%', 'display': 'inline-block',
                'marginBottom': '2.5%'
            }
        )
    ]),
    html.Div([
        html.Div(
            'Agility:',
            style={
                'width': '40%', 'display': 'inline-block',
                'fontWeight': 'bold'
            }
        ),
        dbc.Input(
            type='number', value=536, id='unbuffed_agi',
            style={
                'width': '30%', 'display': 'inline-block',
                'marginBottom': '2.5%'
            }
        )
    ]),
    html.Div([
        html.Div(
            'Intellect:',
            style={
                'width': '40%', 'display': 'inline-block',
                'fontWeight': 'bold'
            }
        ),
        dbc.Input(
            type='number', value=233, id='unbuffed_int',
            style={
                'width': '30%', 'display': 'inline-block',
                'marginBottom': '2.5%'
            }
        )
    ]),
    html.Div([
        html.Div(
            'Spirit:',
            style={
                'width': '40%', 'display': 'inline-block',
                'marginBottom': '0%', 'fontWeight': 'bold'
            }
        ),
        dbc.Input(
            value=153, type='number', id='unbuffed_spirit',
            style={
                'width': '30%', 'display': 'inline-block',
                'marginBottom': '2.5%', 'marginRight': '5%'
            }
        ),
    ]),
    html.Br(),
    html.Div([
        html.Div(
            'Attack Power:',
            style={
                'width': '40%', 'display': 'inline-block',
                'fontWeight': 'bold'
            }
        ),
        dbc.Input(
            type='number', value=3070, id='unbuffed_attack_power',
            style={
                'width': '30%', 'display': 'inline-block',
                'marginBottom': '2.5%'
            }
        )
    ]),
    html.Div([
        html.Div(
            'Added Weapon Damage',
            style={
                'width': '40%', 'display': 'inline-block',
                'fontWeight': 'bold'
            }
        ),
        dbc.Input(
            type='number', value=9, id='weapon_damage',
            style={
                'width': '30%', 'display': 'inline-block',
                'marginBottom': '2.5%'
            }
        )
    ]),
    html.Div([
        html.Div(
            'Crit Chance:',
            style={
                'width': '40%', 'display': 'inline-block',
                'marginBottom': '0%', 'fontWeight': 'bold'
            }
        ),
        dbc.Input(
            type='number', value=36.48, id='unbuffed_crit',
            style={
                'width': '30%', 'display': 'inline-block',
                'marginBottom': '2.5%', 'marginRight': '5%'
            },
            min=0.0, max=100.0, step=0.01
        ),
        html.Div(
            '%',
            style={
                'width': '25%', 'display': 'inline-block',
                'textAlign': 'left'
            }
        )
    ]),
    html.Div([
        html.Div(
            'Hit Chance:',
            style={
                'width': '40%', 'display': 'inline-block',
                'marginBottom': '0%', 'fontWeight': 'bold'
            }
        ),
        dbc.Input(
            type='number', value=5.45, id='unbuffed_hit',
            style={
                'width': '30%', 'display': 'inline-block',
                'marginBottom': '2.5%', 'marginRight': '5%'
            },
            min=0.0, max=9.0, step=0.01
        ),
        html.Div(
            '%',
            style={
                'width': '25%', 'display': 'inline-block',
                'textAlign': 'left'
            }
        )
    ]),
    html.Div([
        html.Div(
            'Haste Rating:',
            style={
                'width': '40%', 'display': 'inline-block',
                'fontWeight': 'bold'
            }
        ),
        dbc.Input(
            type='number', value=0, id='haste_rating',
            style={
                'width': '30%', 'display': 'inline-block',
                'marginBottom': '2.5%'
            }
        )
    ]),
    html.Div([
        html.Div(
            'Armor Penetration:',
            style={
                'width': '40%', 'display': 'inline-block',
                'fontWeight': 'bold'
            }
        ),
        dbc.Input(
            type='number', value=0, id='armor_pen',
            style={
                'width': '30%', 'display': 'inline-block',
                'marginBottom': '2.5%'
            }
        )
    ]),
    html.Div([
        html.Div(
            'Expertise Rating:',
            style={
                'width': '40%', 'display': 'inline-block',
                'fontWeight': 'bold'
            }
        ),
        dbc.Input(
            type='number', value=45, id='expertise_rating',
            style={
                'width': '30%', 'display': 'inline-block',
                'marginBottom': '2.5%'
            }
        )
    ]),
    html.Div([
        html.Div(
            'Equipped weapon speed:',
            style={
                'width': '40%', 'display': 'inline-block',
                'marginBottom': '0%', 'fontWeight': 'bold'
            }
        ),
        dbc.Input(
            value=2.0, type='number', id='unbuffed_weapon_speed',
            style={
                'width': '30%', 'display': 'inline-block',
                'marginBottom': '2.5%', 'marginRight': '5%'
            },
            min=0.1, max=5.0, step=0.1
        ),
        html.Div(
            'seconds',
            style={
                'width': '25%', 'display': 'inline-block',
                'textAlign': 'left'
            }
        )
    ]),
    html.Div([
        html.Div(
            'Mana:',
            style={
                'width': '40%', 'display': 'inline-block',
                'marginBottom': '0%', 'fontWeight': 'bold'
            }
        ),
        dbc.Input(
            value=5585, type='number', id='unbuffed_mana',
            style={
                'width': '30%', 'display': 'inline-block',
                'marginBottom': '2.5%', 'marginRight': '5%'
            }
        ),
    ]),
    html.Div([
        html.Div(
            'MP5:',
            style={
                'width': '40%', 'display': 'inline-block',
                'marginBottom': '0%', 'fontWeight': 'bold'
            }
        ),
        dbc.Input(
            value=0, type='number', id='unbuffed_mp5',
            style={
                'width': '30%', 'display': 'inline-block',
                'marginBottom': '2.5%', 'marginRight': '5%'
            }
        ),
    ]),
    ], width='auto', style={'marginBottom': '2.5%', 'marginLeft': '2.5%'})

buffs_1 = dbc.Col(
    [html.H5('Consumables'),
     dbc.Checklist(
         options=[{'label': 'Elixir of Major Agility', 'value': 'agi_elixir'},
                  {'label': 'Warp Burger / Grilled Mudfish', 'value': 'food'},
                  {'label': 'Scroll of Agility V', 'value': 'scroll_agi'},
                  {'label': 'Scroll of Strength V', 'value': 'scroll_str'},
                  {'label': 'Consecrated Sharpening Stone', 'value': 'consec'},
                  {'label': 'Adamantite Weightstone', 'value': 'weightstone'},
                  {'label': 'Dark / Demonic Rune', 'value': 'rune'}],
         value=[
             'agi_elixir', 'food', 'scroll_agi', 'scroll_str', 'weightstone',
             'rune'
         ],
         id='consumables'
     ),
     dbc.InputGroup(
         [
             dbc.InputGroupAddon('Potion CD:', addon_type='prepend'),
             dbc.Select(
                 options=[
                     {'label': 'Super Mana Potion', 'value': 'super'},
                     {'label': 'Fel Mana Potion', 'value': 'fel'},
                     {'label': 'Haste Potion', 'value': 'haste'},
                     {'label': 'None', 'value': 'none'},
                 ],
                 value='super', id='potion',
             ),
         ],
         style={'width': '50%', 'marginTop': '1.5%'}
     ),
     html.Br(),
     html.H5('Raid Buffs'),
     dbc.Checklist(
         options=[{'label': 'Blessing of Kings', 'value': 'kings'},
                  {'label': 'Blessing of Might', 'value': 'might'},
                  {'label': 'Mark of the Wild', 'value': 'motw'},
                  {'label': 'Trueshot Aura', 'value': 'trueshot_aura'},
                  {'label': 'Improved Sanctity Aura', 'value': 'sanc_aura'},
                  {'label': 'Strength of Earth Totem', 'value': 'str_totem'},
                  {'label': 'Grace of Air Totem', 'value': 'agi_totem'},
                  {'label': 'Arcane Intellect', 'value': 'ai'},
                  {'label': 'Prayer of Spirit', 'value': 'spirit'},
                  {'label': 'Blessing of Wisdom', 'value': 'wisdom'},
                  {'label': 'Battle Shout', 'value': 'bshout'}],
         value=[
             'kings', 'might', 'motw', 'str_totem', 'agi_totem', 'ai',
             'spirit',
         ],
         id='raid_buffs'
     ),
     dbc.Checklist(
         options=[{'label': 'Commanding Presence', 'value': 'talent'},
                  {'label': "Solarian's Sapphire", 'value': 'trinket'}],
         value=[], id='bshout_options',
         style={'marginLeft': '5%'},
     ),
     html.Br(),
     html.H5('Other Buffs'),
     dbc.Row(
         [dbc.Col(dbc.Checklist(
             options=[{'label': 'Manual Crowd Pummeler - Maximum uses:',
                       'value': 'mcp'},
                      {'label': 'Bloodlust', 'value': 'lust'},
                      {'label': 'Omen of Clarity', 'value': 'omen'},
                      {'label': 'Bogling Root', 'value': 'bogling_root'},
                      {'label': 'Unleashed Rage', 'value': 'unleashed_rage'},
                      {'label': 'Heroic Presence', 'value': 'heroic_presence'},
                      {
                          'label': 'Braided Eternium Chain',
                          'value': 'be_chain'
                      }],
             value=['omen', 'be_chain'], id='other_buffs',
          ), width='auto'),
          dbc.Col(dbc.Input(
              value=2, type='number', id='num_mcp',
              style={'width': '35%', 'marginTop': '-5%'}
          ))],
     ),
     dbc.InputGroup(
         [
             dbc.InputGroupAddon(
                 'Ferocious Inspiration stacks:', addon_type='prepend'
             ),
             dbc.Input(
                 value=2, type='number', id='ferocious_inspiration', min=0,
                 max=4
             )
         ],
         style={'width': '45%', 'marginTop': '2%'}, size='sm'
     )],
    width='auto', style={'marginBottom': '2.5%', 'marginLeft': '2.5%'}
)

encounter_details = dbc.Col(
    [html.H5('Idols and Set Bonuses'),
     dbc.Checklist(
         options=[{'label': 'Idol of the Raven Goddess', 'value': 'raven'}],
         value=[], id='raven_idol'
     ),
     dbc.Checklist(
         options=[{'label': 'Everbloom Idol', 'value': 'everbloom'},
                  {'label': '2-piece Tier 4 bonus', 'value': 't4_bonus'},
                  {'label': '4-piece Tier 5 bonus', 'value': 't5_bonus'},
                  {'label': '2-piece Tier 6 bonus', 'value': 't6_2p'},
                  {'label': '4-piece Tier 6 bonus', 'value': 't6_4p'}],
         value=['everbloom', 't5_bonus'],
         id='bonuses'
     ),
     html.Br(),
     html.H4('Encounter Details'),
     dbc.InputGroup(
         [
             dbc.InputGroupAddon('Fight Length:', addon_type='prepend'),
             dbc.Input(
                 value=180.0, type='number', id='fight_length',
             ),
             dbc.InputGroupAddon('seconds', addon_type='append')
         ],
         style={'width': '75%'}
     ),
     dbc.InputGroup(
         [
             dbc.InputGroupAddon('Boss Armor:', addon_type='prepend'),
             dbc.Input(value=7700, type='number', id='boss_armor')
         ],
         style={'width': '75%'}
     ),
     html.Br(),
     html.H5('Damage Debuffs'),
     dbc.Checklist(
         options=[
             {'label': 'Gift of Arthas', 'value': 'gift_of_arthas'},
             {'label': 'Sunder Armor', 'value': 'sunder'},
             {'label': 'Improved Expose Armor', 'value': 'imp_EA'},
             {'label': 'Curse of Recklessness', 'value': 'CoR'},
             {'label': 'Faerie Fire', 'value': 'faerie_fire'},
             {'label': 'Annihilator', 'value': 'annihilator'},
             {'label': 'Blood Frenzy', 'value': 'blood_frenzy'},
         ],
         value=[
             'sunder', 'imp_EA', 'CoR', 'faerie_fire', 'blood_frenzy'
         ],
         id='boss_debuffs'
     ),
     html.Br(),
     html.H5('Stat Debuffs'),
     dbc.Checklist(
         options=[
             {'label': 'Improved Faerie Fire', 'value': 'imp_ff'},
             {'label': "Improved Hunter's Mark", 'value': 'hunters_mark'},
             {'label': 'Improved Judgment of the Crusader', 'value': 'jotc'},
             {'label': 'Judgment of Wisdom', 'value': 'jow'},
             {'label': 'Expose weakness', 'value': 'expose'},
         ],
         value=['imp_ff', 'hunters_mark', 'jow', 'expose'],
         id='stat_debuffs',
     ),
     dbc.InputGroup(
         [
             dbc.InputGroupAddon(
                 'Survival hunter Agility:', addon_type='prepend'
             ),
             dbc.Input(value=1000, type='number', id='surv_agi',),
         ],
         size='sm',
         style={'width': '60%', 'marginTop': '2%', 'marginLeft': '10%'},
     )],
    width='auto', style={'marginLeft': '2.5%', 'marginBottom': '2.5%'}
)

# Sim replicates input
iteration_input = dbc.Col([
    html.H4('Sim Settings'),
    html.Div(
        'Number of replicates:',
        style={
            'width': '40%', 'display': 'inline-block', 'fontWeight': 'bold'
        }
    ),
    dbc.Input(
        type='number', value=20000, id='num_replicates',
        style={
            'width': '50%', 'display': 'inline-block', 'marginBottom': '2.5%'
        }
    ),
    html.Br(),
    html.H5('Talents'),
    html.Div([
        html.Div(
            'Feral Aggression:',
            style={
                'width': '35%', 'display': 'inline-block',
                'fontWeight': 'bold'
            }
        ),
        dbc.Select(
            options=[
                {'label': '0', 'value': 0},
                {'label': '1', 'value': 1},
                {'label': '2', 'value': 2},
                {'label': '3', 'value': 3},
                {'label': '4', 'value': 4},
                {'label': '5', 'value': 5},
            ],
            value='0', id='feral_aggression',
            style={
                'width': '35%', 'display': 'inline-block',
                'marginBottom': '2.5%', 'marginRight': '5%'
            }
        )]),
    html.Div([
        html.Div(
            'Savage Fury:',
            style={
                'width': '35%', 'display': 'inline-block',
                'fontWeight': 'bold'
            }
        ),
        dbc.Select(
            options=[
                {'label': '0', 'value': 0},
                {'label': '1', 'value': 1},
                {'label': '2', 'value': 2},
            ],
            value=2, id='savage_fury',
            style={
                'width': '35%', 'display': 'inline-block',
                'marginBottom': '2.5%', 'marginRight': '5%'
            }
        )]),
    html.Div([
        html.Div(
            'Naturalist:',
            style={
                'width': '35%', 'display': 'inline-block',
                'fontWeight': 'bold'
            }
        ),
        dbc.Select(
            options=[
                {'label': '0', 'value': 0},
                {'label': '1', 'value': 1},
                {'label': '2', 'value': 2},
                {'label': '3', 'value': 3},
                {'label': '4', 'value': 4},
                {'label': '5', 'value': 5},
            ],
            value=5, id='naturalist',
            style={
                'width': '35%', 'display': 'inline-block',
                'marginBottom': '2.5%', 'marginRight': '5%'
            }
        )]),
    html.Div([
        html.Div(
            'Natural Shapeshifter:',
            style={
                'width': '35%', 'display': 'inline-block',
                'fontWeight': 'bold'
            }
        ),
        dbc.Select(
            options=[
                {'label': '0', 'value': 0},
                {'label': '1', 'value': 1},
                {'label': '2', 'value': 2},
                {'label': '3', 'value': 3},
            ],
            value=3, id='natural_shapeshifter',
            style={
                'width': '35%', 'display': 'inline-block',
                'marginBottom': '2.5%', 'marginRight': '5%'
            }
        )]),
    html.Div([
        html.Div(
            'Intensity:',
            style={
                'width': '35%', 'display': 'inline-block',
                'fontWeight': 'bold'
            }
        ),
        dbc.Select(
            options=[
                {'label': '0', 'value': 0},
                {'label': '1', 'value': 1},
                {'label': '2', 'value': 2},
                {'label': '3', 'value': 3},
            ],
            value=3, id='intensity',
            style={
                'width': '35%', 'display': 'inline-block',
                'marginBottom': '2.5%', 'marginRight': '5%'
            }
        )]),
    html.Br(),
    html.H5('Player Strategy'),
    dbc.InputGroup(
        [
            dbc.InputGroupAddon('Finishing move:', addon_type='prepend'),
            dbc.Select(
                options=[
                    {'label': 'Rip', 'value': 'rip'},
                    {'label': 'Ferocious Bite', 'value': 'bite'},
                    {'label': 'None', 'value': 'none'},
                ],
                value='rip', id='finisher',
            ),
        ],
        style={'width': '45%', 'marginBottom': '1.5%'}
    ),
    dbc.InputGroup(
        [
            dbc.InputGroupAddon(
                'Minimum combo points for Rip:', addon_type='prepend'
            ),
            dbc.Select(
                options=[
                    {'label': '4', 'value': 4},
                    {'label': '5', 'value': 5},
                ],
                value=5, id='rip_cp',
            ),
        ],
        style={'width': '48%', 'marginBottom': '1.5%'}
    ),
    dbc.InputGroup(
        [
            dbc.InputGroupAddon(
                'Minimum combo points for Ferocious Bite:',
                addon_type='prepend'
            ),
            dbc.Select(
                options=[
                    {'label': '4', 'value': 4},
                    {'label': '5', 'value': 5},
                ],
                value=5, id='bite_cp',
            ),
        ],
        style={'width': '60%', 'marginBottom': '1.5%'}
    ),
    dbc.InputGroup(
        [
            dbc.InputGroupAddon('Wait at most:', addon_type='prepend'),
            dbc.Input(
                value=1.0, min=0.0, max=2.0, step=0.1, type='number',
                id='max_wait_time',
            ),
            dbc.InputGroupAddon(
                'seconds for an energy tick', addon_type='append'
            )
        ],
        style={'width': '63%', 'marginBottom': '1.5%'}
    ),
    dbc.InputGroup(
        [
            dbc.InputGroupAddon('Wait', addon_type='prepend'),
            dbc.Input(
                value=15.0, min=0.0, step=0.5, type='number', id='cd_delay',
            ),
            dbc.InputGroupAddon(
                'seconds before using cooldowns', addon_type='append'
            ),
        ],
        style={'width': '63%'},
    ),
    html.Br(),
    dbc.Row([
        dbc.Col(dbc.Checklist(
            options=[{'label': " pre-pop Tiger's Fury", 'value': 'prepop_TF'}],
            value=[], id='prepop_TF',
        ), width='auto'),
        dbc.Col('at', width='auto'),
        dbc.Col(dbc.Select(
            options=[{'label': '1', 'value': 1}, {'label': '2', 'value': 2}],
            value=2, id='prepop_numticks',
            style={'marginTop': '-7%'},
        ), width='auto'),
        dbc.Col('energy ticks before combat', width='auto')
    ],),
    dbc.Checklist(
        options=[{'label': ' use Mangle trick', 'value': 'use_mangle_trick'}],
        value=['use_mangle_trick'], id='use_mangle_trick'
    ),
    dbc.Checklist(
        options=[{'label': ' use Innervate', 'value': 'use_innervate'}],
        value=[], id='use_innervate'
    ),
    dbc.Row([
        dbc.Col(dbc.Checklist(
            options=[{'label': " use Ferocious Bite with", 'value': 'bite'}],
            value=['bite'], id='use_bite',
        ), width='auto'),
        dbc.Col('with', width='auto'),
        dbc.Col(dbc.Input(
            type='number', value=0, id='bite_time', min=0.0, step=0.1,
            style={'marginTop': '-7%', 'width': '40%'},
        ), width='auto'),
        dbc.Col(
            'seconds left on Rip', width='auto', style={'marginLeft': '-20%'}
        )
    ],),
    dbc.Checklist(
        options=[{
            'label': ' Mangle maintained by bear tank', 'value': 'bear_mangle'
        }], value=[], id='bear_mangle'
    ),
    html.Br(),
    html.H5('Trinkets'),
    dbc.Row([
        dbc.Col(dbc.Select(
            id='trinket_1',
            options=[
                {'label': 'Empty', 'value': 'none'},
                {'label': 'Tsunami Talisman', 'value': 'tsunami'},
                {'label': 'Bloodlust Brooch', 'value': 'brooch'},
                {'label': 'Hourglass of the Unraveller', 'value': 'hourglass'},
                {'label': 'Dragonspine Trophy', 'value': 'dst'},
                {'label': 'Mark of the Champion', 'value': 'motc'},
                {'label': "Slayer's Crest", 'value': 'slayers'},
                {'label': 'Drake Fang Talisman', 'value': 'dft'},
                {'label': 'Icon of Unyielding Courage', 'value': 'icon'},
                {'label': 'Abacus of Violent Odds', 'value': 'abacus'},
                {'label': 'Badge of the Swarmguard', 'value': 'swarmguard'},
                {'label': 'Kiss of the Spider', 'value': 'kiss'},
                {'label': 'Badge of Tenacity', 'value': 'tenacity'},
                {
                    'label': 'Living Root of the Wildheart',
                    'value': 'class_trinket',
                },
                {'label': 'Crystalforged Trinket', 'value': 'crystalforged'},
                {'label': 'Madness of the Betrayer', 'value': 'madness'},
            ],
            value='brooch'
        )),
        dbc.Col(dbc.Select(
            id='trinket_2',
            options=[
                {'label': 'Empty', 'value': 'none'},
                {'label': 'Tsunami Talisman', 'value': 'tsunami'},
                {'label': 'Bloodlust Brooch', 'value': 'brooch'},
                {'label': 'Hourglass of the Unraveller', 'value': 'hourglass'},
                {'label': 'Dragonspine Trophy', 'value': 'dst'},
                {'label': 'Mark of the Champion', 'value': 'motc'},
                {'label': "Slayer's Crest", 'value': 'slayers'},
                {'label': 'Drake Fang Talisman', 'value': 'dft'},
                {'label': 'Icon of Unyielding Courage', 'value': 'icon'},
                {'label': 'Abacus of Violent Odds', 'value': 'abacus'},
                {'label': 'Badge of the Swarmguard', 'value': 'swarmguard'},
                {'label': 'Kiss of the Spider', 'value': 'kiss'},
                {'label': 'Badge of Tenacity', 'value': 'tenacity'},
                {
                    'label': 'Living Root of the Wildheart',
                    'value': 'class_trinket',
                },
                {'label': 'Crystalforged Trinket', 'value': 'crystalforged'},
                {'label': 'Madness of the Betrayer', 'value': 'madness'},
            ],
            value='tsunami'
        )),
    ]),
    html.Div(
        'Make sure not to include passive trinket stats in the sim input.',
        style={'marginTop': '2.5%'},
    ),
    html.Div([
        dbc.Button(
            "Run", id='run_button', n_clicks=0, size='lg', color='success',
            style={
                'marginBottom': '10%', 'fontSize': 'large', 'marginTop': '10%',
                'display': 'inline-block'
            }
        ),
        html.Div(
            '', id='status',
            style={
                'display': 'inline-block', 'fontWeight': 'bold',
                'marginLeft': '10%', 'fontSize': 'large'
            }
        )
    ]),
    dcc.Interval(id='interval', interval=500),
], width='auto', style={'marginBottom': '2.5%', 'marginLeft': '2.5%'})

input_layout = html.Div(children=[
    html.H1(
        children='WoW Classic TBC Feral Cat Simulator',
        style={'textAlign': 'center'}
    ),
    dbc.Row(
        [stat_input, buffs_1, encounter_details, iteration_input],
        style={'marginTop': '2.5%'}
    ),
])

stats_output = dbc.Col(
    [html.H4('Raid Buffed Stats'),
     html.Div([
         html.Div(
             'Swing Timer:',
             style={'width': '50%', 'display': 'inline-block',
                    'fontWeight': 'bold', 'fontSize': 'large'}
         ),
         html.Div(
             '',
             style={'width': '50%', 'display': 'inline-block',
                    'fontSize': 'large'},
             id='buffed_swing_timer'
         )
     ]),
     html.Div([
         html.Div(
             'Attack Power:',
             style={'width': '50%', 'display': 'inline-block',
                    'fontWeight': 'bold', 'fontSize': 'large'}
         ),
         html.Div(
             '',
             style={'width': '50%', 'display': 'inline-block',
                    'fontSize': 'large'},
             id='buffed_attack_power'
         )
     ]),
     html.Div([
         html.Div(
             'Boss Crit Chance:',
             style={'width': '50%', 'display': 'inline-block',
                    'fontWeight': 'bold', 'fontSize': 'large'}
         ),
         html.Div(
             '',
             style={'width': '50%', 'display': 'inline-block',
                    'fontSize': 'large'},
             id='buffed_crit'
         )
     ]),
     html.Div([
         html.Div(
             'Boss Miss Chance:',
             style={'width': '50%', 'display': 'inline-block',
                    'fontWeight': 'bold', 'fontSize': 'large'}
         ),
         html.Div(
             '',
             style={'width': '50%', 'display': 'inline-block',
                    'fontSize': 'large'},
             id='buffed_miss'
         )
     ]),
     html.Div([
         html.Div(
             'Mana:',
             style={'width': '50%', 'display': 'inline-block',
                    'fontWeight': 'bold', 'fontSize': 'large'}
         ),
         html.Div(
             '',
             style={'width': '50%', 'display': 'inline-block',
                    'fontSize': 'large'},
             id='buffed_mana'
         )
     ]),
     html.Div([
         html.Div(
             'Intellect:',
             style={'width': '50%', 'display': 'inline-block',
                    'fontWeight': 'bold', 'fontSize': 'large'}
         ),
         html.Div(
             '',
             style={'width': '50%', 'display': 'inline-block',
                    'fontSize': 'large'},
             id='buffed_int'
         )
     ]),
     html.Div([
         html.Div(
             'Spirit:',
             style={'width': '50%', 'display': 'inline-block',
                    'fontWeight': 'bold', 'fontSize': 'large'}
         ),
         html.Div(
             '',
             style={'width': '50%', 'display': 'inline-block',
                    'fontSize': 'large'},
             id='buffed_spirit'
         )
     ]),
     html.Div([
         html.Div(
             'MP5:',
             style={'width': '50%', 'display': 'inline-block',
                    'fontWeight': 'bold', 'fontSize': 'large'}
         ),
         html.Div(
             '',
             style={'width': '50%', 'display': 'inline-block',
                    'fontSize': 'large'},
             id='buffed_mp5'
         )
     ])],
    width=4, xl=3, style={'marginLeft': '2.5%', 'marginBottom': '2.5%'}
)

sim_output = dbc.Col([
    html.H4('Results'),
    dcc.Loading(children=html.Div([
        html.Div(
            'Average DPS:',
            style={
                'width': '50%', 'display': 'inline-block',
                'fontWeight': 'bold', 'fontSize': 'large'
            }
        ),
        html.Div(
            '',
            style={
                'width': '50%', 'display': 'inline-block', 'fontSize': 'large'
            },
            id='mean_std_dps'
        ),
    ]), id='loading_1', type='default'),
    dcc.Loading(children=html.Div([
        html.Div(
            'Median DPS:',
            style={
                'width': '50%', 'display': 'inline-block',
                'fontWeight': 'bold', 'fontSize': 'large'
            }
        ),
        html.Div(
            '',
            style={
                'width': '50%', 'display': 'inline-block', 'fontSize': 'large'
            },
            id='median_dps'
        ),
    ]), id='loading_2', type='default'),
    dcc.Loading(children=html.Div([
        html.Div(
            'Time to oom:',
            style={
                'width': '50%', 'display': 'inline-block',
                'fontWeight': 'bold', 'fontSize': 'large'
            }
        ),
        html.Div(
            '',
            style={
                'width': '50%', 'display': 'inline-block', 'fontSize': 'large'
            },
            id='time_to_oom'
        ),
    ]), id='loading_oom_time', type='default'),
    html.Br(),
    html.H5('DPS Breakdown'),
    dcc.Loading(children=dbc.Table([
        html.Thead(html.Tr([
            html.Th('Ability'), html.Th('Number of Casts'),
            html.Th('Average DPS'), html.Th('DPS Contribution')
        ])),
        html.Tbody(id='dps_breakdown_table')
    ]), id='loading_3', type='default'),
    html.Br(),
    html.Br()
], style={'marginLeft': '2.5%', 'marginBottom': '2.5%'}, width=4, xl=3)

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
                    dbc.FormGroup(
                        [
                            dbc.Checkbox(
                                id='calc_mana_weights',
                                className='form-check-input'
                            ),
                            dbc.Label(
                                'Include mana weights',
                                html_for='calc_mana_weights',
                                className='form-check-label'
                            )
                        ],
                        check=True
                    ),
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

sim_section = dbc.Row(
    [stats_output, sim_output, weights_section]
)

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

app.layout = html.Div([
    input_layout, sim_section, graph_section
])


# Helper functions used in master callback
def process_trinkets(trinket_1, trinket_2, player, ap_mod, stat_mod, cd_delay):
    proc_trinkets = []
    all_trinkets = []

    for trinket in [trinket_1, trinket_2]:
        if trinket == 'none':
            continue

        trinket_params = copy.deepcopy(trinkets.trinket_library[trinket])

        for stat, increment in trinket_params['passive_stats'].items():
            if stat == 'attack_power':
                increment *= ap_mod

            setattr(player, stat, getattr(player, stat) + increment)

        if trinket_params['type'] == 'passive':
            continue

        active_stats = trinket_params['active_stats']

        if active_stats['stat_name'] == 'attack_power':
            active_stats['stat_increment'] *= ap_mod
        if active_stats['stat_name'] == 'Agility':
            active_stats['stat_name'] = ['attack_power', 'crit_chance']
            agi_increment = active_stats['stat_increment']
            active_stats['stat_increment'] = np.array([
                stat_mod * agi_increment * ap_mod,
                stat_mod * agi_increment/25./100.
            ])
        if active_stats['stat_name'] == 'Strength':
            active_stats['stat_name'] = 'attack_power'
            active_stats['stat_increment'] *= 2 * stat_mod * ap_mod

        if trinket_params['type'] == 'activated':
            # If this is the second trinket slot and the first trinket was also
            # activated, then we need to enforce an activation delay due to the
            # shared cooldown. For now we will assume that the shared cooldown
            # is always equal to the duration of the first trinket's proc.
            if all_trinkets and (not proc_trinkets):
                delay = cd_delay + all_trinkets[-1].proc_duration
            else:
                delay = cd_delay

            all_trinkets.append(
                trinkets.ActivatedTrinket(delay=delay, **active_stats)
            )
        else:
            proc_type = active_stats.pop('proc_type')

            if proc_type == 'chance_on_hit':
                proc_chance = active_stats.pop('proc_rate')
                active_stats['chance_on_hit'] = proc_chance
                active_stats['chance_on_crit'] = proc_chance
            elif proc_type == 'chance_on_crit':
                active_stats['chance_on_hit'] = 0.0
                active_stats['chance_on_crit'] = active_stats.pop('proc_rate')
            elif proc_type == 'ppm':
                ppm = active_stats.pop('proc_rate')
                active_stats['chance_on_hit'] = ppm/60.
                active_stats['yellow_chance_on_hit'] = (
                    ppm/60. * player.weapon_speed
                )

            if trinket == 'swarmguard':
                trinket_obj = trinkets.BadgeOfTheSwarmguard(
                    active_stats['chance_on_hit'],
                    active_stats['yellow_chance_on_hit']
                )
            elif trinket_params['type'] == 'refreshing_proc':
                trinket_obj = trinkets.RefreshingProcTrinket(**active_stats)
            else:
                trinket_obj = trinkets.ProcTrinket(**active_stats)

            all_trinkets.append(trinket_obj)
            proc_trinkets.append(all_trinkets[-1])

    player.proc_trinkets = proc_trinkets
    return all_trinkets


def create_buffed_player(
        unbuffed_strength, unbuffed_agi, unbuffed_int, unbuffed_spirit,
        unbuffed_ap, unbuffed_crit, unbuffed_hit, haste_rating,
        expertise_rating, armor_pen, weapon_damage, weapon_speed,
        unbuffed_mana, unbuffed_mp5, consumables, raid_buffs, bshout_options,
        num_mcp, other_buffs, stat_debuffs, surv_agi, feral_aggression,
        savage_fury, naturalist, natural_shapeshifter, ferocious_inspiration,
        intensity, potion, bonuses, raven_idol
):
    """Compute fully raid buffed stats based on specified raid buffs, and
    instantiate a Player object with those stats."""

    # Swing timer calculation is independent of other buffs. First we add up
    # the haste rating from all the specified haste buffs
    use_mcp = ('mcp' in other_buffs) and (num_mcp > 0)
    buffed_haste_rating = haste_rating + 500 * use_mcp
    buffed_swing_timer = ccs.calc_swing_timer(buffed_haste_rating)

    # Determine "raw" AP, crit, and mana not from Str/Agi/Int
    raw_ap_unbuffed = unbuffed_ap / 1.1 - 2 * unbuffed_strength - unbuffed_agi
    raw_crit_unbuffed = unbuffed_crit - unbuffed_agi / 25
    raw_mana_unbuffed = unbuffed_mana - 15 * unbuffed_int

    # Augment all base stats based on specified buffs
    stat_multiplier = 1 + 0.1 * ('kings' in raid_buffs)
    added_stats = 18.9 * ('motw' in raid_buffs)

    buffed_strength = stat_multiplier * (unbuffed_strength + 1.03 * (
        added_stats + 88.55 * ('str_totem' in raid_buffs)
        + 20 * ('scroll_str' in consumables)
    ))
    buffed_agi = stat_multiplier * (unbuffed_agi + 1.03 * (
        added_stats + 88.55 * ('agi_totem' in raid_buffs)
        + 35 * ('agi_elixir' in consumables) + 20 * ('food' in consumables)
        + 20 * ('scroll_agi' in consumables)
    ))
    buffed_int = stat_multiplier * (
        unbuffed_int + 1.2 * 1.03 * (added_stats + 40 * ('ai' in raid_buffs))
    )
    buffed_spirit = stat_multiplier * (unbuffed_spirit + 1.03 * (
        added_stats + 50 * ('spirit' in raid_buffs)
        + 20 * ('food' in consumables)
    ))

    # Now augment secondary stats
    ap_mod = 1.1 * (1 + 0.1 * ('unleashed_rage' in other_buffs))
    bshout_ap = (
        ('bshout' in raid_buffs) * (306 + 70 * ('trinket' in bshout_options))
        * (1. + 0.25 * ('talent' in bshout_options))
    )
    buffed_attack_power = ap_mod * (
        raw_ap_unbuffed + 2 * buffed_strength + buffed_agi
        + 222 * ('might' in raid_buffs) + bshout_ap
        + 100 * ('trueshot_aura' in raid_buffs)
        + 100 * ('consec' in consumables)
        + 110 * ('hunters_mark' in stat_debuffs)
        + 0.25 * surv_agi * ('expose' in stat_debuffs)
    )
    added_crit_rating = (
        20 * ('agi_elixir' in consumables)
        + 14 * ('weightstone' in consumables)
        + 28 * ('be_chain' in other_buffs)
        + 20 * bool(raven_idol)
    )
    buffed_crit = (
        raw_crit_unbuffed + buffed_agi / 25 + 3 * ('jotc' in stat_debuffs)
        + added_crit_rating / 22.1
    )
    buffed_hit = (
        unbuffed_hit + 3 * ('imp_ff' in stat_debuffs)
        + 1 * ('heroic_presence' in other_buffs)
    )
    buffed_mana_pool = raw_mana_unbuffed + buffed_int * 15
    buffed_mp5 = unbuffed_mp5 + 39.6 * ('wisdom' in raid_buffs)

    # Calculate bonus damage parameters
    bonus_weapon_damage = (
        12 * ('weightstone' in consumables) + ('bogling_root' in other_buffs)
        + weapon_damage
    )
    damage_multiplier = (
        (1 + 0.02 * int(naturalist)) * 1.03**ferocious_inspiration
        * (1 + 0.02 * ('sanc_aura' in raid_buffs))
    )
    shred_bonus = 88 * ('everbloom' in bonuses) + 75 * ('t5_bonus' in bonuses)

    # Create and return a corresponding Player object
    player = ccs.Player(
        attack_power=buffed_attack_power, hit_chance=buffed_hit / 100,
        expertise_rating=expertise_rating, crit_chance=buffed_crit / 100,
        swing_timer=buffed_swing_timer, mana=buffed_mana_pool,
        intellect=buffed_int, spirit=buffed_spirit, mp5=buffed_mp5,
        omen='omen' in other_buffs, feral_aggression=int(feral_aggression),
        savage_fury=int(savage_fury),
        natural_shapeshifter=int(natural_shapeshifter),
        intensity=int(intensity), weapon_speed=weapon_speed,
        bonus_damage=bonus_weapon_damage, multiplier=damage_multiplier,
        jow='jow' in stat_debuffs, armor_pen=armor_pen,
        t4_bonus='t4_bonus' in bonuses, t6_2p='t6_2p' in bonuses,
        t6_4p='t6_4p' in bonuses, rune='rune' in consumables,
        pot=potion in ['super', 'fel'], cheap_pot=(potion == 'super'),
        shred_bonus=shred_bonus
    )
    return player, ap_mod, stat_multiplier * 1.03


def run_sim(sim, num_replicates):
    # Run the sim for the specified number of replicates
    dps_vals, dmg_breakdown, oom_times = sim.run_replicates(
        num_replicates, detailed_output=True
    )

    # Consolidate DPS statistics
    avg_dps = np.mean(dps_vals)
    mean_dps_str = '%.1f +/- %.1f' % (avg_dps, np.std(dps_vals))
    median_dps_str = '%.1f' % np.median(dps_vals)

    # Consolidate mana statistics
    avg_oom_time = np.mean(oom_times)

    if avg_oom_time > sim.fight_length - 1:
        oom_time_str = 'none'
    else:
        oom_time_str = (
            '%d +/- %d seconds' % (avg_oom_time, np.std(oom_times))
        )

    # Create DPS breakdown table
    table = []

    for ability in dmg_breakdown:
        if ability in ['Claw']:
            continue

        ability_dps = dmg_breakdown[ability]['damage'] / sim.fight_length
        table.append(html.Tr([
            html.Td(ability),
            html.Td('%.3f' % dmg_breakdown[ability]['casts']),
            html.Td('%.3f' % ability_dps),
            html.Td('%.1f%%' % (ability_dps / avg_dps * 100))
        ]))

    return avg_dps, (mean_dps_str, median_dps_str, oom_time_str, table)


def append_mana_weights(
        weights_table, sim, num_replicates, time_to_oom, avg_dps, dps_per_AP,
        stat_multiplier
):
    # Just set all mana weights to 0 if we didn't even go oom
    if time_to_oom == 'none':
        weights_table.append(html.Tr([
            html.Td('mana stats'), html.Td('0.0'), html.Td('0.0'),
        ]))
        return

    # Calculate DPS increases and weights
    dps_deltas, stat_weights = sim.calc_mana_weights(
        num_replicates, avg_dps, dps_per_AP
    )

    # Parse results
    for stat in dps_deltas:
        multiplier = 1.0 if stat in ['1 mana', '1 mp5'] else stat_multiplier
        weights_table.append(html.Tr([
            html.Td(stat),
            html.Td('%.3f' % (dps_deltas[stat] * multiplier)),
            html.Td('%.3f' % (stat_weights[stat] * multiplier)),
        ]))


def calc_weights(
        sim, num_replicates, avg_dps, calc_mana_weights, time_to_oom,
        raid_buffs, unleashed_rage
):
    # Check that sufficient iterations are used for convergence.
    if num_replicates < 20000:
        error_msg = (
            'Stat weight calculation requires the simulation to be run with at'
            ' least 20,000 replicates.'
        )
        return 'Error: ', error_msg, [], ''

    # Do fresh weights calculation
    weights_table = []

    # Calculate DPS increases and weights
    dps_deltas, stat_weights = sim.calc_stat_weights(
        num_replicates, base_dps=avg_dps, unleashed_rage=unleashed_rage
    )

    # Parse results
    for stat in dps_deltas:
        if stat == '1 AP':
            weight = 1.0
            dps_per_AP = dps_deltas[stat]
        else:
            weight = stat_weights[stat]

        weights_table.append(html.Tr([
            html.Td(stat),
            html.Td('%.2f' % dps_deltas[stat]),
            html.Td('%.2f' % weight),
        ]))

    # Generate 70upgrades import link for raw stats
    stat_multiplier = (1 + 0.1 * ('kings' in raid_buffs)) * 1.03
    url = ccs.gen_import_link(stat_weights, multiplier=stat_multiplier)
    link = html.A('Seventy Upgrades Import Link', href=url, target='_blank')

    # Only calculate mana stats if requested
    if calc_mana_weights:
        append_mana_weights(
            weights_table, sim, num_replicates, time_to_oom, avg_dps,
            dps_per_AP, stat_multiplier
        )

    return 'Stat Breakdown', '', weights_table, link


def plot_new_trajectory(sim, show_whites):
    t_vals, _, energy_vals, cp_vals, _, log = sim.run(log=True)
    t_fine = np.linspace(0, sim.fight_length, 10000)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t_fine, y=ccs.piecewise_eval(t_fine, t_vals, energy_vals),
        line=dict(color="#d62728")
    ))
    fig.add_trace(go.Scatter(
        x=t_fine, y=ccs.piecewise_eval(t_fine, t_vals, cp_vals),
        line=dict(color="#9467bd", dash='dash'), yaxis='y2'
    ))
    fig.update_layout(
        xaxis=dict(title='Time (seconds)'),
        yaxis=dict(
            title='Energy', titlefont=dict(color='#d62728'),
            tickfont=dict(color='#d62728')
        ),
        yaxis2=dict(
            title='Combo points', titlefont=dict(color='#9467bd'),
            tickfont=dict(color='#9467bd'), anchor='x', overlaying='y',
            side='right'
        ),
        showlegend=False,
    )

    # Create combat log table
    log_table = []

    if not show_whites:
        parsed_log = [row for row in log if row[1] != 'melee']
    else:
        parsed_log = log

    for row in parsed_log:
        log_table.append(html.Tr([
            html.Td(entry) for entry in row
        ]))

    return fig, log_table


# Master callback function
@app.callback(
    Output('buffed_swing_timer', 'children'),
    Output('buffed_attack_power', 'children'),
    Output('buffed_crit', 'children'),
    Output('buffed_miss', 'children'),
    Output('buffed_mana', 'children'),
    Output('buffed_int', 'children'),
    Output('buffed_spirit', 'children'),
    Output('buffed_mp5', 'children'),
    Output('mean_std_dps', 'children'),
    Output('median_dps', 'children'),
    Output('time_to_oom', 'children'),
    Output('dps_breakdown_table', 'children'),
    Output('error_str', 'children'),
    Output('error_msg', 'children'),
    Output('stat_weight_table', 'children'),
    Output('import_link', 'children'),
    Output('energy_flow', 'figure'),
    Output('combat_log', 'children'),
    Input('unbuffed_strength', 'value'),
    Input('unbuffed_agi', 'value'),
    Input('unbuffed_int', 'value'),
    Input('unbuffed_spirit', 'value'),
    Input('unbuffed_attack_power', 'value'),
    Input('unbuffed_crit', 'value'),
    Input('unbuffed_hit', 'value'),
    Input('haste_rating', 'value'),
    Input('armor_pen', 'value'),
    Input('expertise_rating', 'value'),
    Input('unbuffed_weapon_speed', 'value'),
    Input('unbuffed_mana', 'value'),
    Input('unbuffed_mp5', 'value'),
    Input('consumables', 'value'),
    Input('raid_buffs', 'value'),
    Input('bshout_options', 'value'),
    Input('num_mcp', 'value'),
    Input('other_buffs', 'value'),
    Input('raven_idol', 'value'),
    Input('stat_debuffs', 'value'),
    Input('surv_agi', 'value'),
    Input('trinket_1', 'value'),
    Input('trinket_2', 'value'),
    Input('run_button', 'n_clicks'),
    Input('weight_button', 'n_clicks'),
    Input('graph_button', 'n_clicks'),
    State('weapon_damage', 'value'),
    State('potion', 'value'),
    State('ferocious_inspiration', 'value'),
    State('bonuses', 'value'),
    State('feral_aggression', 'value'),
    State('savage_fury', 'value'),
    State('naturalist', 'value'),
    State('natural_shapeshifter', 'value'),
    State('intensity', 'value'),
    State('fight_length', 'value'),
    State('boss_armor', 'value'),
    State('boss_debuffs', 'value'),
    State('finisher', 'value'),
    State('rip_cp', 'value'),
    State('bite_cp', 'value'),
    State('max_wait_time', 'value'),
    State('cd_delay', 'value'),
    State('prepop_TF', 'value'),
    State('prepop_numticks', 'value'),
    State('use_mangle_trick', 'value'),
    State('use_innervate', 'value'),
    State('use_bite', 'value'),
    State('bite_time', 'value'),
    State('bear_mangle', 'value'),
    State('num_replicates', 'value'),
    State('calc_mana_weights', 'checked'),
    State('show_whites', 'checked'))
def compute(
        unbuffed_strength, unbuffed_agi, unbuffed_int, unbuffed_spirit,
        unbuffed_ap, unbuffed_crit, unbuffed_hit, haste_rating, armor_pen,
        expertise_rating, weapon_speed, unbuffed_mana, unbuffed_mp5,
        consumables, raid_buffs, bshout_options, num_mcp, other_buffs,
        raven_idol, stat_debuffs, surv_agi, trinket_1, trinket_2, run_clicks,
        weight_clicks, graph_clicks, weapon_damage, potion,
        ferocious_inspiration, bonuses, feral_aggression, savage_fury,
        naturalist, natural_shapeshifter, intensity, fight_length, boss_armor,
        boss_debuffs, finisher, rip_cp, bite_cp, max_wait_time, cd_delay,
        prepop_TF, prepop_numticks, use_mangle_trick, use_innervate, use_bite,
        bite_time, bear_mangle, num_replicates, calc_mana_weights, show_whites
):
    ctx = dash.callback_context

    # Create Player object based on specified stat inputs and talents
    player, ap_mod, stat_mod = create_buffed_player(
        unbuffed_strength, unbuffed_agi, unbuffed_int, unbuffed_spirit,
        unbuffed_ap, unbuffed_crit, unbuffed_hit, haste_rating,
        expertise_rating, armor_pen, weapon_damage, weapon_speed,
        unbuffed_mana, unbuffed_mp5, consumables, raid_buffs, bshout_options,
        num_mcp, other_buffs, stat_debuffs, surv_agi, feral_aggression,
        savage_fury, naturalist, natural_shapeshifter, ferocious_inspiration,
        intensity, potion, bonuses, raven_idol
    )

    # Process trinkets
    trinket_list = process_trinkets(
        trinket_1, trinket_2, player, ap_mod, stat_mod, cd_delay
    )

    # Default output is just the buffed player stats with no further calcs
    stats_output = (
        '%.3f seconds' % player.swing_timer,
        '%d' % player.attack_power,
        '%.2f %%' % (player.crit_chance * 100),
        '%.2f %%' % (player.miss_chance * 100),
        '%d' % player.mana_pool, '%d' % player.intellect,
        '%d' % player.spirit, '%d' % player.mp5
    )

    # Create Simulation object based on specified parameters
    max_mcp = num_mcp if 'mcp' in other_buffs else 0
    bite = (bool(use_bite) and (finisher == 'rip')) or (finisher == 'bite')
    rip_combos = 6 if finisher != 'rip' else int(rip_cp)

    if 'lust' in other_buffs:
        trinket_list.append(trinkets.Bloodlust(delay=cd_delay))

    if potion == 'haste':
        haste_pot = trinkets.HastePotion(delay=cd_delay)
    else:
        haste_pot = None

    sim = ccs.Simulation(
        player, fight_length + 1e-9, num_mcp=max_mcp,
        boss_armor=boss_armor, prepop_TF=bool(prepop_TF),
        prepop_numticks=int(prepop_numticks), min_combos_for_rip=rip_combos,
        min_combos_for_bite=int(bite_cp), use_innervate=bool(use_innervate),
        use_mangle_trick=bool(use_mangle_trick), use_bite=bite,
        bite_time=bite_time, bear_mangle=bool(bear_mangle),
        trinkets=trinket_list, max_wait_time=max_wait_time, haste_pot=haste_pot
    )
    sim.set_active_debuffs(boss_debuffs)
    player.calc_damage_params(**sim.params)

    # If either "Run" or "Stat Weights" button was pressed, then perform a
    # sim run for the specified number of replicates.
    if (ctx.triggered and
            (ctx.triggered[0]['prop_id'] in
             ['run_button.n_clicks', 'weight_button.n_clicks'])):
        avg_dps, dps_output = run_sim(sim, num_replicates)
    else:
        dps_output = ('', '', '', [])

    # If "Stat Weights" button was pressed, then calculate weights.
    if (ctx.triggered and
            (ctx.triggered[0]['prop_id'] == 'weight_button.n_clicks')):
        weights_output = calc_weights(
            sim, num_replicates, avg_dps, calc_mana_weights, dps_output[2],
            raid_buffs, 'unleashed_rage' in other_buffs
        )
    else:
        weights_output = ('Stat Breakdown', '', [], '')

    # If "Generate Example" button was pressed, do it.
    if (ctx.triggered and
            (ctx.triggered[0]['prop_id'] == 'graph_button.n_clicks')):
        example_output = plot_new_trajectory(sim, show_whites)
    else:
        example_output = ({}, [])

    return stats_output + dps_output + weights_output + example_output


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app.run_server(
        host='0.0.0.0', port=8080, debug=False
    )
