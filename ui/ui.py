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
from ui.graph import graph_section
from ui.weights import weights_section
from ui.defaults import default_input_stats
from ui.inputs import stat_input, encounter_details, buffs_1, generate_input_layout
from ui.outputs import sim_output, stats_output, generate_gear_output
from ui.util.buffs import apply_buffs
from ui.util.plot import plot_new_trajectory, calc_weights
from ui.util import trinkets

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

def uses_wolfshead(input_json):
    for i in input_json['items']:
        if i['slot'] == "HEAD":
            if "wolfshead" in i['name']:
                return True
    return False

class UI:
    df = None
    def __init__(self):
        self.df = pd.DataFrame(columns=[
            "dps",
            "name",
            "trinket 1",
            "trinket 2",
            "wolfshead",
            "crit",
            "hit",
            "ap",
            "expertise",
            "armorPen",
            "link"
        ])
        self.app = app
        self.sim_section = dbc.Row(
            [stats_output, sim_output, weights_section]
        )
        self.app.callback(
                    Output('upload_status', 'children'),
                    Output('upload_status', 'style'),
                    Output('buff_section', 'is_open'),
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
                    Output('aura_breakdown_table', 'children'),
                    Output('error_str', 'children'),
                    Output('error_msg', 'children'),
                    Output('stat_weight_table', 'children'),
                    Output('import_link', 'children'),
                    Output('energy_flow', 'figure'),
                    Output('combat_log', 'children'),
                    Input('upload-data', 'contents'),
                    Input('paste-data', 'value'),
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
                    State('cooldowns', 'value'),
                    State('finisher', 'value'),
                    State('rip_cp', 'value'),
                    State('bite_cp', 'value'),
                    State('max_wait_time', 'value'),
                    State('cd_delay', 'value'),
                    State('prepop_TF', 'value'),
                    State('prepop_numticks', 'value'),
                    State('use_mangle_trick', 'value'),
                    State('use_rake_trick', 'value'),
                    State('use_bite_trick', 'value'),
                    State('bite_trick_cp', 'value'),
                    State('bite_trick_max', 'value'),
                    State('use_innervate', 'value'),
                    State('use_biteweave', 'value'),
                    State('bite_time', 'value'),
                    State('use_ripweave', 'value'),
                    State('ripweave_energy', 'value'),
                    State('bear_mangle', 'value'),
                    State('num_replicates', 'value'),
                    State('latency', 'value'),
                    State('calc_mana_weights', 'checked'),
                    State('epic_gems', 'checked'),
                    State('show_whites', 'checked'))(self.compute)

        self.app.callback(
            Output('use_rake_trick', 'options'),
            Output('use_bite_trick', 'options'),
            Output('use_rake_trick', 'labelStyle'),
            Output('use_bite_trick', 'labelStyle'),
            Output('bite_trick_text_1', 'style'),
            Output('bite_trick_text_2', 'style'),
            Input('bonuses', 'value'),
            Input('use_rake_trick', 'value'),
            Input('use_bite_trick', 'value'))(self.disable_tricks)

        self.app.callback(
            Output('use_biteweave', 'options'),
            Output('use_biteweave', 'labelStyle'),
            Output('biteweave_text_1', 'style'),
            Output('biteweave_text_2', 'style'),
            Output('use_ripweave', 'options'),
            Output('use_ripweave', 'labelStyle'),
            Output('ripweave_text_1', 'style'),
            Output('ripweave_text_2', 'style'),
            Input('finisher', 'value'))(self.disable_weaves)

        self.app.callback(
            Output("gear_output", "data"),
            Output("gear_output", 'columns'),
            Input("gear_output", "sort_by"),
            Input("median_dps", "children"))(self.update_table)

        self.app.layout = html.Div([
            generate_input_layout(), self.sim_section, generate_gear_output, graph_section
        ])

    def process_trinkets(self, input_json, trinket_1, trinket_2, player, ap_mod, stat_mod, cd_delay):
        print(trinket_1, trinket_2)
        print(type(trinket_1))
        if trinket_1 == 'none':
            if input_json is not None:
                for i in input_json['items']:
                    if i['slot'] == 'TRINKET_1':
                        print("TRINKET_1: {}".format(i['name']))
                        trinket_1 = trinkets.trinket_map[i['name']]
        if trinket_2 == 'none':
            if input_json is not None:
                for i in input_json['items']:
                    if i['slot'] == 'TRINKET_2':
                        trinket_2 = trinkets.trinket_map[i['name']]

        proc_trinkets = []
        all_trinkets = []

        print(trinket_1, trinket_2)
        for trinket in [trinket_1, trinket_2]:
            if trinket == 'none':
                continue

            trinket_params = copy.deepcopy(trinkets.trinket_library[trinket])

            for stat, increment in trinket_params['passive_stats'].items():
                if stat == 'intellect':
                    increment *= 1.2  # hardcode the HotW 20% increase
                if stat in ['strength', 'agility', 'intellect', 'spirit']:
                    increment *= stat_mod
                if stat == 'strength':
                    increment *= 2
                    stat = 'attack_power'
                if stat == 'agility':
                    stat = 'attack_power'
                    # additionally modify crit here
                    setattr(
                        player, 'crit_chance',
                        getattr(player, 'crit_chance') + increment / 25. / 100.
                    )
                if stat == 'attack_power':
                    increment *= ap_mod
                if stat == 'haste_rating':
                    new_swing_timer = ccs.calc_swing_timer(
                        ccs.calc_haste_rating(player.swing_timer) + increment,
                        )
                    player.swing_timer = new_swing_timer
                    continue

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
                    stat_mod * agi_increment / 25. / 100.
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
                    active_stats['chance_on_hit'] = ppm / 60.
                    active_stats['yellow_chance_on_hit'] = (
                            ppm / 60. * player.weapon_speed
                    )

                if trinket == 'vial':
                    trinket_obj = trinkets.PoisonVial(
                        active_stats['chance_on_hit'],
                        active_stats['yellow_chance_on_hit']
                    )
                elif trinket_params['type'] == 'refreshing_proc':
                    trinket_obj = trinkets.RefreshingProcTrinket(**active_stats)
                elif trinket_params['type'] == 'stacking_proc':
                    trinket_obj = trinkets.StackingProcTrinket(**active_stats)
                else:
                    trinket_obj = trinkets.ProcTrinket(**active_stats)

                all_trinkets.append(trinket_obj)
                proc_trinkets.append(all_trinkets[-1])

        player.proc_trinkets = proc_trinkets
        return all_trinkets

    def create_player(self,
            buffed_attack_power, buffed_hit, buffed_crit, buffed_weapon_damage,
            haste_rating, expertise_rating, armor_pen, buffed_mana_pool,
            buffed_int, buffed_spirit, buffed_mp5, weapon_speed, unleashed_rage,
            kings, raven_idol, other_buffs, stat_debuffs, cooldowns, num_mcp,
            surv_agi, ferocious_inspiration, bonuses, naturalist, feral_aggression,
            savage_fury, natural_shapeshifter, intensity, potion
    ):
        """Takes in raid buffed player stats from Seventy Upgrades, modifies them
        based on boss debuffs and miscellaneous buffs not captured by Seventy
        Upgrades, and instantiates a Player object with those stats."""

        # Swing timer calculation is independent of other buffs. First we add up
        # the haste rating from all the specified haste buffs
        use_mcp = ('mcp' in cooldowns) and (num_mcp > 0)
        buffed_haste_rating = haste_rating + 500 * use_mcp
        buffed_swing_timer = ccs.calc_swing_timer(buffed_haste_rating)

        # Augment secondary stats as needed
        ap_mod = 1.1 * (1 + 0.1 * unleashed_rage)
        debuff_ap = (
                100 * ('consec' in other_buffs)
                + 110 * ('hunters_mark' in stat_debuffs)
                + 0.25 * surv_agi * ('expose' in stat_debuffs)
        )
        encounter_crit = (
                buffed_crit + 3 * ('jotc' in stat_debuffs)
                + (28 * ('be_chain' in other_buffs) + 20 * bool(raven_idol)) / 22.1
        )
        encounter_hit = buffed_hit + 3 * ('imp_ff' in stat_debuffs)
        encounter_mp5 = buffed_mp5 + 50 * ('mana_spring_totem' in other_buffs)

        # Calculate bonus damage parameters
        encounter_weapon_damage = (
                buffed_weapon_damage + ('bogling_root' in other_buffs)
        )
        damage_multiplier = (
                (1 + 0.02 * int(naturalist)) * 1.03**ferocious_inspiration
                * (1 + 0.02 * ('sanc_aura' in other_buffs))
        )
        shred_bonus = 88 * ('everbloom' in bonuses) + 75 * ('t5_bonus' in bonuses)

        # Create and return a corresponding Player object
        player = ccs.Player(
            attack_power=buffed_attack_power, hit_chance=encounter_hit / 100,
            expertise_rating=expertise_rating, crit_chance=encounter_crit / 100,
            swing_timer=buffed_swing_timer, mana=buffed_mana_pool,
            intellect=buffed_int, spirit=buffed_spirit, mp5=encounter_mp5,
            omen='omen' in other_buffs, feral_aggression=int(feral_aggression),
            savage_fury=int(savage_fury),
            natural_shapeshifter=int(natural_shapeshifter),
            intensity=int(intensity), weapon_speed=weapon_speed,
            bonus_damage=encounter_weapon_damage, multiplier=damage_multiplier,
            jow='jow' in stat_debuffs, armor_pen=armor_pen,
            t4_bonus='t4_bonus' in bonuses, t6_2p='t6_2p' in bonuses,
            t6_4p='t6_4p' in bonuses, wolfshead='wolfshead' in bonuses,
            meta='meta' in bonuses, rune='rune' in cooldowns,
            pot=potion in ['super', 'fel'], cheap_pot=(potion == 'super'),
            shred_bonus=shred_bonus, debuff_ap=debuff_ap
        )
        return player, ap_mod, (1 + 0.1 * kings) * 1.03

    def run_sim(self, sim, num_replicates):
        # Run the sim for the specified number of replicates
        dps_vals, dmg_breakdown, aura_stats, oom_times = sim.run_replicates(
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
        dps_table = []

        for ability in dmg_breakdown:
            if ability in ['Claw']:
                continue

            ability_dps = dmg_breakdown[ability]['damage'] / sim.fight_length
            ability_cpm = dmg_breakdown[ability]['casts'] / sim.fight_length * 60.
            ability_dpct = ability_dps * 60. / ability_cpm if ability_cpm else 0.
            dps_table.append(html.Tr([
                html.Td(ability),
                html.Td('%.3f' % dmg_breakdown[ability]['casts']),
                html.Td('%.1f' % ability_cpm),
                html.Td('%.0f' % ability_dpct),
                html.Td('%.1f%%' % (ability_dps / avg_dps * 100))
            ]))

        # Create Aura uptime table
        aura_table = []

        for row in aura_stats:
            aura_table.append(html.Tr([
                html.Td(row[0]),
                html.Td('%.3f' % row[1]),
                html.Td('%.1f%%' % (row[2] * 100))
            ]))

        return (
            avg_dps,
            (mean_dps_str, median_dps_str, oom_time_str, dps_table, aura_table),
        )

    def compute(self,
            json_file, paste_data, consumables, raid_buffs, bshout_options, num_mcp,
            other_buffs, raven_idol, stat_debuffs, surv_agi, trinket_1, trinket_2,
            run_clicks, weight_clicks, graph_clicks, potion, ferocious_inspiration,
            bonuses, feral_aggression, savage_fury, naturalist,
            natural_shapeshifter, intensity, fight_length, boss_armor,
            boss_debuffs, cooldowns, finisher, rip_cp, bite_cp, max_wait_time,
            cd_delay, prepop_TF, prepop_numticks, use_mangle_trick, use_rake_trick,
            use_bite_trick, bite_trick_cp, bite_trick_max, use_innervate,
            use_biteweave, bite_time, use_ripweave, ripweave_energy, bear_mangle,
            num_replicates, latency, calc_mana_weights, epic_gems, show_whites
    ):
        ctx = dash.callback_context

        # Parse input stats JSON
        buffs_present = False
        use_default_inputs = True

        input_json = None
        if json_file is None and paste_data is None:
            upload_output = (
                'No file uploaded, using default input stats instead.',
                {'color': '#E59F3A', 'width': 300}, True
            )
        else:
            try:
                if paste_data:
                    input_json = json.loads(paste_data)
                else:
                    content_type, content_string = json_file.split(',')
                    decoded = base64.b64decode(content_string)
                    input_json = json.load(io.StringIO(decoded.decode('utf-8')))
                buffs_present = input_json['exportOptions']['buffs']
                catform_checked = (
                        ('form' in input_json['exportOptions'])
                        and (input_json['exportOptions']['form'] == 'cat')
                )


                if not catform_checked:
                    upload_output = (
                        'Error processing input file! "Cat Form" was not checked '
                        'in the export pop-up window. Using default input stats '
                        'instead.',
                        {'color': '#D35845', 'width': 300}, True
                    )
                elif buffs_present:
                    pot_present = False

                    for entry in input_json['consumables']:
                        if 'Potion' in entry['name']:
                            pot_present = True

                    if pot_present:
                        upload_output = (
                            'Error processing input file! Potions should not be '
                            'checked in the Seventy Upgrades buff tab, as they are'
                            ' temporary rather than permanent stat buffs. Using'
                            ' default input stats instead.',
                            {'color': '#D35845', 'width': 300}, True
                        )
                    else:
                        upload_output = (
                            'Upload successful. Buffs detected in Seventy Upgrades'
                            ' export, so the "Consumables" and "Raid Buffs" '
                            'sections in the sim input will be ignored.',
                            {'color': '#5AB88F', 'width': 300}, False
                        )
                        use_default_inputs = False
                else:
                    upload_output = (
                        'Upload successful. No buffs detected in Seventy Upgrades '
                        'export, so use the  "Consumables" and "Raid Buffs" '
                        'sections in the sim input for buff entry.',
                        {'color': '#5AB88F', 'width': 300}, True
                    )
                    use_default_inputs = False
            except Exception:
                upload_output = (
                    'Error processing input file! Using default input stats '
                    'instead.',
                    {'color': '#D35845', 'width': 300}, True
                )

        if use_default_inputs:
            input_stats = copy.copy(default_input_stats)
            buffs_present = False
        else:
            input_stats = input_json['stats']



        # If buffs are not specified in the input file, then interpret the input
        # stats as unbuffed and calculate the buffed stats ourselves.
        if not buffs_present:
            input_stats.update(apply_buffs(
                input_stats['attackPower'], input_stats['strength'],
                input_stats['agility'], input_stats['hit'], input_stats['crit'],
                input_stats['mana'], input_stats['intellect'],
                input_stats['spirit'], input_stats.get('mp5', 0),
                input_stats.get('weaponDamage', 0), raid_buffs, consumables,
                bshout_options
            ))

        # Determine whether Unleashed Rage and/or Blessing of Kings are present, as
        # these impact stat weights and buff values.
        if buffs_present:
            unleashed_rage = False
            kings = False

            for buff in input_json['buffs']:
                if buff['name'] == 'Blessing of Kings':
                    kings = True
                if buff['name'] == 'Unleashed Rage':
                    unleashed_rage = True
        else:
            unleashed_rage = 'unleashed_rage' in raid_buffs
            kings = 'kings' in raid_buffs

        # Create Player object based on raid buffed stat inputs and talents
        player, ap_mod, stat_mod = self.create_player(
            input_stats['attackPower'], input_stats['hit'], input_stats['crit'],
            input_stats.get('weaponDamage', 0), input_stats.get('hasteRating', 0),
            input_stats.get('expertiseRating', 0), input_stats.get('armorPen', 0),
            input_stats['mana'], input_stats['intellect'], input_stats['spirit'],
            input_stats.get('mp5', 0), float(input_stats['mainHandSpeed']),
            unleashed_rage, kings, raven_idol, other_buffs, stat_debuffs,
            cooldowns, num_mcp, surv_agi, ferocious_inspiration, bonuses,
            naturalist, feral_aggression, savage_fury, natural_shapeshifter,
            intensity, potion
        )


        # Process trinkets
        trinket_list = self.process_trinkets(input_json,
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
        max_mcp = num_mcp if 'mcp' in cooldowns else 0
        bite = (
                (bool(use_biteweave) and (finisher == 'rip')) or (finisher == 'bite')
        )
        rip_combos = 6 if finisher != 'rip' else int(rip_cp)
        ripweave_combos = 6 if finisher != 'bite' else int(rip_cp)

        if 'lust' in cooldowns:
            trinket_list.append(trinkets.Bloodlust(delay=cd_delay))
        if 'drums' in cooldowns:
            trinket_list.append(trinkets.ActivatedTrinket(
                'haste_rating', 80, 'Drums of Battle', 30, 120, delay=cd_delay
            ))

        if 'exalted_ring' in bonuses:
            ring_ppm = 1.0
            ring = trinkets.ProcTrinket(
                chance_on_hit=ring_ppm / 60.,
                yellow_chance_on_hit=ring_ppm / 60. * player.weapon_speed,
                stat_name='attack_power', stat_increment=160 * ap_mod,
                proc_duration=10, cooldown=60,
                proc_name='Band of the Eternal Champion',
            )
            trinket_list.append(ring)
            player.proc_trinkets.append(ring)
        if 'idol_of_terror' in bonuses:
            idol = trinkets.ProcTrinket(
                chance_on_hit=0.85, stat_name=['attack_power', 'crit_chance'],
                stat_increment=np.array([
                    65. * stat_mod * ap_mod,
                    65. * stat_mod / 25. / 100.,
                    ]),
                proc_duration=10, cooldown=10, proc_name='Primal Instinct',
                mangle_only=True
            )
            trinket_list.append(idol)
            player.proc_trinkets.append(idol)
        if 'stag_idol' in bonuses:
            idol = trinkets.RefreshingProcTrinket(
                chance_on_hit=1.0, stat_name='attack_power',
                stat_increment=94 * ap_mod, proc_duration=20, cooldown=0,
                proc_name='Idol of the White Stag', mangle_only=True
            )
            trinket_list.append(idol)
            player.proc_trinkets.append(idol)

        if potion == 'haste':
            haste_pot = trinkets.HastePotion(delay=cd_delay)
        else:
            haste_pot = None

        sim = ccs.Simulation(
            player, fight_length + 1e-9, 0.001 * latency, num_mcp=max_mcp,
            boss_armor=boss_armor, prepop_TF=bool(prepop_TF),
            prepop_numticks=int(prepop_numticks), min_combos_for_rip=rip_combos,
            min_combos_for_bite=int(bite_cp), use_innervate=bool(use_innervate),
            use_rake_trick=bool(use_rake_trick),
            use_bite_trick=bool(use_bite_trick), bite_trick_cp=int(bite_trick_cp),
            bite_trick_max=bite_trick_max,
            use_mangle_trick=bool(use_mangle_trick), use_bite=bite,
            bite_time=bite_time, use_rip_trick=bool(use_ripweave),
            rip_trick_cp=ripweave_combos, rip_trick_min=ripweave_energy,
            bear_mangle=bool(bear_mangle), trinkets=trinket_list,
            max_wait_time=max_wait_time, haste_pot=haste_pot
        )
        sim.set_active_debuffs(boss_debuffs)
        player.calc_damage_params(**sim.params)

        # If either "Run" or "Stat Weights" button was pressed, then perform a
        # sim run for the specified number of replicates.
        if (ctx.triggered and
                (ctx.triggered[0]['prop_id'] in
                 ['run_button.n_clicks', 'weight_button.n_clicks'])):
            avg_dps, dps_output = self.run_sim(sim, num_replicates)
            self.generate_set_entry(input_json, avg_dps, trinket_1, trinket_2)
        else:
            dps_output = ('', '', '', [], [])

        # If "Stat Weights" button was pressed, then calculate weights.
        if (ctx.triggered and
                (ctx.triggered[0]['prop_id'] == 'weight_button.n_clicks')):
            weights_output = calc_weights(
                sim, num_replicates, avg_dps, calc_mana_weights, dps_output[2],
                kings, unleashed_rage, epic_gems
            )
        else:
            weights_output = ('Stat Breakdown', '', [], '')

        # If "Generate Example" button was pressed, do it.
        if (ctx.triggered and
                (ctx.triggered[0]['prop_id'] == 'graph_button.n_clicks')):
            example_output = plot_new_trajectory(sim, show_whites)
        else:
            example_output = ({}, [])

        return (
                upload_output + stats_output + dps_output + weights_output
                + example_output
        )

    # Callbacks for disabling rotation options when inappropriate
    def disable_tricks(self, bonuses, rake_trick_checked, bite_trick_checked):
        rake_options = {'label': ' use Rake trick', 'value': 'use_rake_trick'}
        bite_options = {'label': ' use Bite trick', 'value': 'use_bite_trick'}
        rake_text_style = {}
        bite_text_style = {}

        if 't6_2p' in bonuses:
            if rake_trick_checked:
                rake_text_style['color'] = '#D35845'
            else:
                rake_options['disabled'] = True
                rake_text_style['color'] = '#888888'

            if bite_trick_checked:
                bite_text_style['color'] = '#D35845'
            else:
                bite_options['disabled'] = True
                bite_text_style['color'] = '#888888'

        return (
            [rake_options], [bite_options], rake_text_style, bite_text_style,
            bite_text_style, bite_text_style
        )


    def disable_weaves(self, finisher):
        biteweave_options = {'label': ' weave Ferocious Bite', 'value': 'bite'}
        ripweave_options = {'label': ' weave Rip', 'value': 'rip'}
        biteweave_text_style_1 = {}
        biteweave_text_style_2 = {'marginLeft': '-15%'}
        ripweave_text_style_1 = {}
        ripweave_text_style_2 = {'marginLeft': '-15%'}

        if finisher != 'rip':
            biteweave_options['disabled'] = True
            biteweave_text_style_1['color'] = '#888888'
            biteweave_text_style_2['color'] = '#888888'

        if finisher != 'bite':
            ripweave_options['disabled'] = True
            ripweave_text_style_1['color'] = '#888888'
            ripweave_text_style_2['color'] = '#888888'

        return (
            [biteweave_options], biteweave_text_style_1, biteweave_text_style_1,
            biteweave_text_style_2, [ripweave_options], ripweave_text_style_1,
            ripweave_text_style_1, ripweave_text_style_2
        )

    def generate_set_entry(self, input_json, dps, trinket_1, trinket_2):
        if trinket_1 == 'none':
            if input_json is not None:
                for i in input_json['items']:
                    if i['slot'] == 'TRINKET_1':
                        print("TRINKET_1: {}".format(i['name']))
                        trinket_1 = trinkets.trinket_map[i['name']]
        if trinket_2 == 'none':
            if input_json is not None:
                for i in input_json['items']:
                    if i['slot'] == 'TRINKET_2':
                        trinket_2 = trinkets.trinket_map[i['name']]
        # add info to the set table
        stats = input_json['stats']
        set_input = {
            "name": input_json['name'],
            "wolfshead": uses_wolfshead(input_json),
            "trinket 1": trinkets.trinket_friendly_name(trinket_1),
            "trinket 2": trinkets.trinket_friendly_name(trinket_2),
            "crit": stats['crit'],
            "hit": stats['hit'],
            "ap": stats["attackPower"],
            "dps": dps}
        if 'set' in input_json['links'].keys():
            #set_input['link'] = "<a href={}>'Link'</a>".format(input_json['links']['set'])
            set_input['link'] = input_json['links']['set']
        else:
            set_input['link'] = "None"
        if 'expertise' in stats:
            set_input['expertise'] = stats['expertise']
        if 'armorPen' in stats:
            set_input['armorPen'] = stats['armorPen']
        self.df = self.df.append(set_input, ignore_index=True)
        print(self.df)

    def update_table(self, sort_by, median_dps):
        print("sort by: {}".format(sort_by))
        if len(sort_by):
            dff = self.df.sort_values(
                sort_by[0]['column_id'],
                ascending=sort_by[0]['direction'] == 'asc',
                inplace=False,
            )
        else:
            dff = self.df

        return dff.to_dict('records'), [{'name': i, 'id': i, 'deletable': True} for i in dff.columns]



    def run_server(self, host="0.0.0.0", port=8080, debug=True):
        multiprocessing.freeze_support()
        self.app.run_server(host=host, port=port, debug=debug)