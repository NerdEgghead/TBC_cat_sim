import numpy as np
import plotly.graph_objects as go
import tbc_cat_sim as ccs
from dash import dash_table, dcc, html

def plot_new_trajectory(sim, show_whites):
    t_vals, _, energy_vals, cp_vals, _, _, log = sim.run(log=True)
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
        kings, unleashed_rage, epic_gems
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
    stat_multiplier = (1 + 0.1 * kings) * 1.03
    url = ccs.gen_import_link(
        stat_weights, multiplier=stat_multiplier, epic_gems=epic_gems
    )
    link = html.A('Seventy Upgrades Import Link', href=url, target='_blank')

    # Only calculate mana stats if requested
    if calc_mana_weights:
        append_mana_weights(
            weights_table, sim, num_replicates, time_to_oom, avg_dps,
            dps_per_AP, stat_multiplier
        )

    return 'Stat Breakdown', '', weights_table, link

