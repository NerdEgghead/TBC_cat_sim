from dash import dash_table, dcc, html
import dash_bootstrap_components as dbc


## stats input
stat_input = dbc.Col([
    html.H5('Seventy Upgrades Input'),
    dcc.Markdown(
        'This simulator uses Seventy Upgrades as its gear selection UI. In '
        'order to use it, create a Seventy Upgrades profile for your character'
        ' and download the gear set using the "Export" button at the top right'
        ' of the character sheet. Make sure that "Cat Form" is selected in the'
        ' export window, and that "Talents" are checked (and set up in your '
        'character sheet).',
        style={'width': 300},
    ),
    dcc.Markdown(
        'Consumables and party/raid buffs can be specified either in the '
        'Seventy Upgrades "Buffs" tab, or in the "Consumables" and "Raid '
        'Buffs " sections in the sim. If the "Buffs" option is checked in the '
        'Seventy Upgrades export window, then the corresponding sections in '
        'the sim input will be ignored.',
        style={'width': 300},
    ),
    dcc.Input(
        id='paste-data',
        placeholder="input seventy upgrades json",
        style={
            'width': '100%',
            'minHeight': '60px',
            'height': 'auto',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '0px'
        }
    ),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select File')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '0px'
        },
        # Don't allow multiple files to be uploaded
        multiple=False
    ),
    html.Br(),
    html.Div(
        'No file uploaded, using default input stats instead.',
        id='upload_status', style={'color': '#E59F3A'}
    ),
    html.Br(),
    html.H5('Idols and Set Bonuses'),
    dbc.Checklist(
        options=[{'label': 'Idol of the Raven Goddess', 'value': 'raven'}],
        value=['raven'], id='raven_idol'
    ),
    dbc.Checklist(
        options=[
            {'label': 'Everbloom Idol', 'value': 'everbloom'},
            {'label': 'Idol of Terror', 'value': 'idol_of_terror'},
            {'label': 'Idol of the White Stag', 'value': 'stag_idol'},
            {'label': '2-piece Tier 4 bonus', 'value': 't4_bonus'},
            {'label': '4-piece Tier 5 bonus', 'value': 't5_bonus'},
            {'label': '2-piece Tier 6 bonus', 'value': 't6_2p'},
            {'label': '4-piece Tier 6 bonus', 'value': 't6_4p'},
            {'label': 'Wolfshead Helm', 'value': 'wolfshead'},
            {'label': 'Relentless Earthstorm Diamond', 'value': 'meta'},
            {'label': 'Band of the Eternal Champion', 'value': 'exalted_ring'},
        ],
        value=['t6_2p', 't6_4p', 'wolfshead', 'exalted_ring'],
        id='bonuses'
    ),
], width='auto', style={'marginBottom': '2.5%', 'marginLeft': '2.5%'})


## buffs input
buffs_1 = dbc.Col(
    [dbc.Collapse([html.H5('Consumables'),
                   dbc.Checklist(
                       options=[{'label': 'Elixir of Major Agility', 'value': 'agi_elixir'},
                                {'label': 'Elixir of Draenic Wisdom', 'value': 'draenic'},
                                {'label': 'Warp Burger / Grilled Mudfish', 'value': 'food'},
                                {'label': 'Scroll of Agility V', 'value': 'scroll_agi'},
                                {'label': 'Scroll of Strength V', 'value': 'scroll_str'},
                                {'label': 'Adamantite Weightstone', 'value': 'weightstone'}],
                       value=[
                           'agi_elixir', 'food', 'scroll_agi', 'scroll_str', 'weightstone',
                       ],
                       id='consumables'
                   ),
                   html.Br(),
                   html.H5('Raid Buffs'),
                   dbc.Checklist(
                       options=[{'label': 'Blessing of Kings', 'value': 'kings'},
                                {'label': 'Blessing of Might', 'value': 'might'},
                                {'label': 'Blessing of Wisdom', 'value': 'wisdom'},
                                {'label': 'Mark of the Wild', 'value': 'motw'},
                                {'label': 'Trueshot Aura', 'value': 'trueshot_aura'},
                                {'label': 'Heroic Presence', 'value': 'heroic_presence'},
                                {'label': 'Strength of Earth Totem', 'value': 'str_totem'},
                                {'label': 'Grace of Air Totem', 'value': 'agi_totem'},
                                {'label': 'Unleashed Rage', 'value': 'unleashed_rage'},
                                {'label': 'Arcane Intellect', 'value': 'ai'},
                                {'label': 'Prayer of Spirit', 'value': 'spirit'},
                                {'label': 'Battle Shout', 'value': 'bshout'}],
                       value=[
                           'kings', 'might', 'motw', 'str_totem', 'agi_totem',
                           'unleashed_rage', 'ai', 'bshout'
                       ],
                       id='raid_buffs'
                   ),
                   dbc.Checklist(
                       options=[{'label': 'Commanding Presence', 'value': 'talent'},
                                {'label': "Solarian's Sapphire", 'value': 'trinket'}],
                       value=['talent'], id='bshout_options',
                       style={'marginLeft': '10%'},
                   ),
                   html.Br()], id='buff_section', is_open=True),
     html.H5('Other Buffs'),
     dbc.Checklist(
         options=[
             {'label': 'Omen of Clarity', 'value': 'omen'},
             {'label': 'Bogling Root', 'value': 'bogling_root'},
             {'label': 'Consecrated Sharpening Stone', 'value': 'consec'},
             {'label': 'Improved Sanctity Aura', 'value': 'sanc_aura'},
             {'label': 'Mana Spring Totem', 'value': 'mana_spring_totem'},
             {'label': 'Braided Eternium Chain', 'value': 'be_chain'},
         ],
         value=['omen', 'sanc_aura', 'mana_spring_totem'], id='other_buffs'
     ),
     dbc.InputGroup(
         [
             dbc.InputGroupAddon(
                 'Ferocious Inspiration stacks:', addon_type='prepend'
             ),
             dbc.Input(
                 value=0, type='number', id='ferocious_inspiration', min=0,
                 max=4
             )
         ],
         style={'width': '100%', 'marginTop': '2%'}, size='sm'
     )],
    width='auto', style={'marginBottom': '2.5%', 'marginLeft': '2.5%'}
)

## encounter details
#TODO add boss fights here.

encounter_details = dbc.Col(
    [html.H4('Encounter Details'),
     dbc.InputGroup(
         [
             dbc.InputGroupAddon('Fight Length:', addon_type='prepend'),
             dbc.Input(
                 value=120.0, type='number', id='fight_length',
             ),
             dbc.InputGroupAddon('seconds', addon_type='append')
         ],
         style={'width': '50%'}
     ),
     dbc.InputGroup(
         [
             dbc.InputGroupAddon('Boss Armor:', addon_type='prepend'),
             dbc.Input(value=6193, type='number', id='boss_armor')
         ],
         style={'width': '50%'}
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
             'gift_of_arthas', 'sunder', 'imp_EA', 'CoR', 'faerie_fire',
             'blood_frenzy'
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
         value=['imp_ff', 'hunters_mark', 'jotc', 'jow', 'expose'],
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
         style={'width': '40%', 'marginTop': '1%', 'marginLeft': '5%'},
     ),
     html.Br(),
     html.H5('Cooldowns'),
     dbc.Row([
         dbc.Col(
             dbc.Checklist(
                 options=[
                     {
                         'label': 'Manual Crowd Pummeler - Maximum uses:',
                         'value': 'mcp',
                     },
                     {'label': 'Bloodlust', 'value': 'lust'},
                     {'label': 'Drums of Battle', 'value': 'drums'},
                     {'label': 'Dark / Demonic Rune', 'value': 'rune'},
                 ],
                 value=['lust', 'drums', 'rune'], id='cooldowns',
             ),
             width='auto',
         ),
         dbc.Col(
             dbc.Input(
                 value=2, type='number', id='num_mcp',
                 style={'width': '35%', 'marginTop': '-5%'},
             )
         )
     ]),
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
                 value='haste', id='potion',
             ),
         ],
         style={'width': '50%', 'marginTop': '1.5%'}
     )],
    width='auto',
    style={
        'marginLeft': '2.5%', 'marginBottom': '2.5%', 'marginRight': '-2.5%'
    }
)

### itteration inputs
def generate_iteration_input():
    return dbc.Col([
    html.H4('Sim Settings'),
    dbc.InputGroup(
        [
            dbc.InputGroupAddon('Number of replicates:', addon_type='prepend'),
            dbc.Input(value=20000, type='number', id='num_replicates')
        ],
        style={'width': '35%'}
    ),
    dbc.InputGroup(
        [
            dbc.InputGroupAddon('Modeled input delay:', addon_type='prepend'),
            dbc.Input(
                value=100, type='number', id='latency', min=1, step=1,
            ),
            dbc.InputGroupAddon('ms', addon_type='append')
        ],
        style={'width': '35%'}
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
                'width': '20%', 'display': 'inline-block',
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
                'width': '20%', 'display': 'inline-block',
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
                'width': '20%', 'display': 'inline-block',
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
                'width': '20%', 'display': 'inline-block',
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
                'width': '20%', 'display': 'inline-block',
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
                    {'label': '3', 'value': 3},
                    {'label': '4', 'value': 4},
                    {'label': '5', 'value': 5},
                ],
                value=4, id='rip_cp',
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
                    {'label': '3', 'value': 3},
                    {'label': '4', 'value': 4},
                    {'label': '5', 'value': 5},
                ],
                value=4, id='bite_cp',
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
            options=[{'label': " weave Ferocious Bite", 'value': 'bite'}],
            value=['bite'], id='use_biteweave',
        ), width='auto'),
        dbc.Col('with', width='auto', id='biteweave_text_1'),
        dbc.Col(dbc.Input(
            type='number', value=0, id='bite_time', min=0.0, step=0.1,
            style={'marginTop': '-3%', 'marginBottom': '7%', 'width': '40%'},
        ), width='auto'),
        dbc.Col(
            'seconds left on Rip', width='auto', style={'marginLeft': '-15%'},
            id='biteweave_text_2'
        )
    ],),
    dbc.Row([
        dbc.Col(dbc.Checklist(
            options=[{'label': " weave Rip", 'value': 'rip'}], value=[],
            id='use_ripweave',
        ), width='auto'),
        dbc.Col('at', width='auto', id='ripweave_text_1'),
        dbc.Col(dbc.Input(
            type='number', value=52, id='ripweave_energy', min=30, step=1,
            style={'marginTop': '-3%', 'marginBottom': '7%', 'width': '40%'},
        ), width='auto'),
        dbc.Col(
            'energy or above', width='auto', style={'marginLeft': '-15%'},
            id='ripweave_text_2'
        )
    ],),
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
        options=[{'label': ' use Rake trick', 'value': 'use_rake_trick'}],
        value=[], id='use_rake_trick'
    ),
    dbc.Row([
        dbc.Col(dbc.Checklist(
            options=[{'label': ' use Bite trick', 'value': 'use_bite_trick'}],
            value=[], id='use_bite_trick'
        ), width='auto'),
        dbc.Col('with at least', width='auto', id='bite_trick_text_1'),
        dbc.Col(dbc.Select(
            options=[{'label':  i, 'value': i} for i in range(1, 6)],
            value=2, id='bite_trick_cp',
            style={'marginTop': '-7%'},
        ), width='auto'),
        dbc.Col(
            'combo points, and an energy range up to', width='auto',
            id='bite_trick_text_2'
        ),
        dbc.Col(dbc.Input(
            type='number', value=39, id='bite_trick_max', min=35, step=1,
            style={'marginTop': '-7%', 'width': '40%'},
        ), width='auto'),
    ]),
    dbc.Checklist(
        options=[{'label': ' use Innervate', 'value': 'use_innervate'}],
        value=[], id='use_innervate'
    ),
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
                    'value': 'wildheart',
                },
                {
                    'label': 'Ashtongue Talisman of Equilibrium',
                    'value': 'ashtongue',
                },
                {'label': 'Crystalforged Trinket', 'value': 'crystalforged'},
                {'label': 'Madness of the Betrayer', 'value': 'madness'},
                {'label': "Romulo's Poison Vial", 'value': 'vial'},
                {
                    'label': 'Steely Naaru Sliver',
                    'value': 'steely_naaru_sliver'
                },
                {'label': 'Shard of Contempt', 'value': 'shard_of_contempt'},
                {'label': "Berserker's Call", 'value': 'berserkers_call'},
                {'label': "Alchemist's Stone", 'value': 'alch'},
                {
                    'label': "Assassin's Alchemist Stone",
                    'value': 'assassin_alch'
                },
                {'label': 'Blackened Naaru Sliver', 'value': 'bns'},
                {'label': 'Darkmoon Card: Crusade', 'value': 'crusade'},
            ],
            value='none'
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
                    'value': 'wildheart',
                },
                {
                    'label': 'Ashtongue Talisman of Equilibrium',
                    'value': 'ashtongue',
                },
                {'label': 'Crystalforged Trinket', 'value': 'crystalforged'},
                {'label': 'Madness of the Betrayer', 'value': 'madness'},
                {'label': "Romulo's Poison Vial", 'value': 'vial'},
                {
                    'label': 'Steely Naaru Sliver',
                    'value': 'steely_naaru_sliver'
                },
                {'label': 'Shard of Contempt', 'value': 'shard_of_contempt'},
                {'label': "Berserker's Call", 'value': 'berserkers_call'},
                {'label': "Alchemist's Stone", 'value': 'alch'},
                {
                    'label': "Assassin's Alchemist Stone",
                    'value': 'assassin_alch'
                },
                {'label': 'Blackened Naaru Sliver', 'value': 'bns'},
                {'label': 'Darkmoon Card: Crusade', 'value': 'crusade'},
            ],
            value='none'
        )),
    ]),
    html.Div(
        'Make sure not to include passive trinket stats in the sim input.',
        style={
            'marginTop': '2.5%', 'fontSize': 'large', 'fontWeight': 'bold'
        },
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

def generate_input_layout():
    return html.Div(children=[
    html.H1(
        children='WoW Classic TBC Feral Cat Simulator',
        style={'textAlign': 'center'}
    ),
    dbc.Row(
        [stat_input, buffs_1, encounter_details, generate_iteration_input()],
        style={'marginTop': '2.5%'}
    ),
])
