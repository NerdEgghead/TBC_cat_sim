"""Code for simulating the classic WoW feral cat DPS rotation."""

import numpy as np
import copy
import collections


def calc_white_damage(low_end, high_end, miss_chance, crit_chance):
    """Execute single roll table for a melee white attack.

    Arguments:
        low_end (float): Low end base damage of the swing.
        high_end (float): High end base damage of the swing.
        miss_chance (float): Probability that the swing is avoided.
        crit_chance (float): Probability of a critical strike.

    Returns:
        damage_done (float): Damage done by the swing.
        miss (bool): True if the attack was avoided.
        crit (bool): True if the attack was a critical strike.
    """
    outcome_roll = np.random.rand()

    if outcome_roll < miss_chance:
        return 0.0, True, False

    base_dmg = low_end + np.random.rand() * (high_end - low_end)

    if outcome_roll < miss_chance + 0.24:
        glance_reduction = 0.15 + np.random.rand() * 0.2
        return (1.0 - glance_reduction) * base_dmg, False, False
    if outcome_roll < miss_chance + 0.24 + crit_chance:
        return 2.2 * base_dmg, False, True
    return base_dmg, False, False


def calc_yellow_damage(low_end, high_end, miss_chance, crit_chance):
    """Execute 2-roll table for a melee spell.

    Arguments:
        low_end (float): Low end base damage of the ability.
        high_end (float): High end base damage of the ability.
        miss_chance (float): Probability that the ability is avoided.
        crit_chance (float): Probability of a critical strike.

    Returns:
        damage_done (float): Damage done by the ability.
        miss (bool): True if the attack was avoided.
        crit (bool): True if the attack was a critical strike.
    """
    miss_roll = np.random.rand()

    if miss_roll < miss_chance:
        return 0.0, True, False

    base_dmg = low_end + np.random.rand() * (high_end - low_end)
    crit_roll = np.random.rand()

    if crit_roll < crit_chance:
        return 2.2 * base_dmg, False, True
    return base_dmg, False, False


def piecewise_eval(t_fine, times, values):
    """Evaluate a piecewise constant function on a finer time mesh.

    Arguments:
        t_fine (np.ndarray): Desired mesh for evaluation.
        times (np.ndarray): Breakpoints of piecewise function.
        values (np.ndarray): Function values at the breakpoints.

    Returns:
        y_fine (np.ndarray): Function evaluated on the desired mesh.
    """
    result = np.zeros_like(t_fine)

    for i in range(len(times) - 1):
        result += values[i] * ((t_fine >= times[i]) & (t_fine < times[i + 1]))

    result += values[-1] * (t_fine >= times[-1])

    return result


def calc_swing_timer(haste_rating):
    """Calculate cat swing timer given a total haste rating stat.

    Arguments:
        haste_rating (int): Player haste rating stat.

    Returns:
        swing_timer (float): Hasted swing timer in seconds.
    """
    return 1.0 / (1 + haste_rating / 1577)


def calc_haste_rating(swing_timer):
    """Calculate the haste rating that is consistent with a given swing timer.

    Arguments:
        swing_timer (float): Hasted swing timer in seconds.

    Returns:
        haste_rating (float): Unrounded haste rating.
    """
    return 1577 * (1 / swing_timer - 1)


class Player():

    """Stores damage parameters, energy, combo points, and cooldowns for a
    simulated player in a boss encounter. Executes events in the cat DPS
    rotation."""

    def __init__(
            self, attack_power, hit_chance, crit_chance, armor_pen,
            swing_timer, mana, intellect, spirit, mp5, jow=False, pot=True,
            cheap_pot=False, rune=True, t4_bonus=False, bonus_damage=0,
            shred_bonus=0, multiplier=1.1, omen=True, feral_aggression=0,
            savage_fury=2, natural_shapeshifter=3, intensity=3,
            weapon_speed=3.0, log=False
    ):
        """Initialize player with key damage parameters.

        Arguments:
            attack_power (int): Fully raid buffed attack power.
            hit_chance (float): Chance to hit as a fraction. Values above 9%
                can be used as a proxy for expertise rating on top of hit cap.
            crit_chance (float): Fully raid buffed crit chance as a fraction.
            armor_pen (int): Armor penetration from gear. Boss armor debuffs
                are handled by Simulation objects as they are not properties of
                the player character.
            swing_timer (float): Melee swing timer in seconds, including haste
                effects such as MCP, Warchief's Blessing, and libram enchants.
            mana (int): Fully raid buffed mana.
            intellect (int): Fully raid buffed Intellect.
            spirit (int): Fully raid buffed Spirit.
            mp5 (int): Bonus mp5 from gear or buffs.
            jow (bool): Whether the player is receiving Judgment of Wisdom
                procs. Defaults False.
            pot (bool): Whether mana potions are used. Defaults True.
            cheap_pot (bool): Whether the budget Super Mana Potion is used
                instead of the optimal Fel Mana Potion. Defaults False.
            rune (bool): Whether Dark/Demonic Runes are used. Defaults True.
            t4_bonus (bool): Whether the 2-piece T4 set bonus is used. Defaults
                False.
            bonus_damage (int): Bonus weapon damage from buffs such as Bogling
                Root or Dense Weightstone. Defaults to 0.
            shred_bonus (int): Bonus damage to Shred ability from Idols and set
                bonuses. Defaults to 0.
            multiplier (float): Overall damage multiplier from talents and
                buffs. Defaults to 1.1 (from 5/5 Naturalist).
            omen (bool): Whether Omen of Clarity is active. Defaults True.
            feral_aggression (int): Points taken in Feral Aggression talent.
                Defaults to 2.
            savage_fury (int): Points taken in Savage Fury talent. Defaults
                to 0.
            natural_shapeshifter (int): Points taken in Natural Shapeshifter
                talent. Defaults to 3.
            intensity (int): Points taken in Intensity talen. Defaults to 3.
            weapon_speed (float): Equipped weapon speed, used for calculating
                Omen of Clarity proc rate. Defaults to 3.0.
            log (bool): If True, maintain a log of the most recent event,
                formatted as a list of strings [event, outcome, energy, combo
                points]. Defaults False.
        """
        self.attack_power = attack_power
        self.miss_chance = 0.09 - hit_chance + 0.065
        self.crit_chance = crit_chance - 0.048
        self.armor_pen = armor_pen
        self.swing_timer = swing_timer
        self.mana_pool = mana
        self.intellect = intellect
        self.spirit = spirit
        self.mp5 = mp5
        self.jow = jow
        self.pot = pot
        self.cheap_pot = cheap_pot
        self.rune = rune
        self.t4_bonus = t4_bonus
        self.bonus_damage = bonus_damage
        self.shred_bonus = shred_bonus
        self.damage_multiplier = multiplier
        self.omen = omen
        self.feral_aggression = feral_aggression
        self.savage_fury = savage_fury
        self.natural_shapeshifter = natural_shapeshifter
        self.intensity = intensity
        self.omen_rates = {
            'white': 2.0/60,
            'yellow': 2.0/60 * weapon_speed
        }
        self.set_mana_regen()
        self.log = log
        self.reset()

    def set_mana_regen(self):
        """Calculate and store mana regeneration rates based on specified regen
        stats.
        """
        # Mana regen is still linear in Spirit for TBC, but the scaling
        # coefficient is now Int-dependent.
        self.regen_factor = 0.009327 * np.sqrt(self.intellect) * 2
        base_regen = self.spirit * self.regen_factor
        bonus_regen = self.mp5 / 5 * 2

        # In TBC, the Intensity talent allows a portion of the base regen to
        # apply while within the five second rule
        self.regen_rates = {
            'base': base_regen + bonus_regen,
            'five_second_rule': 0.1*self.intensity*base_regen + bonus_regen,
            'innervated': 5 * base_regen + bonus_regen
        }
        self.shift_cost = 830 * (1 - 0.1 * self.natural_shapeshifter)

        # Since Fel Mana pots regen over time rather than instantaneously, we
        # need to use a more sophisticated heuristic for when to pop it.
        # We pop the potion when our mana has decreased by 1.5x the value at
        # which we would be exactly topped off on average after the 24 second
        # pot duration, factoring in other regen sources and mana spent on
        # shifting. This provides buffer against rng with respect to JoW procs
        # or the number of shift cycles completed in that time.

        if self.cheap_pot:
            self.pot_threshold = self.mana_pool - 3000
            return

        self.pot_threshold = self.mana_pool - 36 * (
            400./3 + self.regen_rates['five_second_rule'] / 2
            + 37. * (1./self.swing_timer + 2./5) - self.shift_cost/5
        )

    def set_active_buffs(self, buff_list):
        """Set active buffs according to a specified list.

        Arguments:
            buff_list (list): List of strings containing buff names. At
                present, "omen" and "bogling_root" are supported.
        """
        all_buffs = ['omen', 'bogling_root']
        active_buffs = copy.copy(buff_list)

        for buff in all_buffs:
            if buff in buff_list:
                setattr(self, buff, True)
                active_buffs.remove(buff)
            else:
                setattr(self, buff, False)

        if active_buffs:
            raise ValueError(
                'Unsupported buffs found: %s. Supported buffs are: %s.' % (
                    active_buffs, all_buffs)
            )

    def calc_damage_params(
            self, gift_of_arthas, boss_armor, sunder, imp_EA, CoR, faerie_fire,
            annihilator, blood_frenzy, tigers_fury=False
    ):
        """Calculate high and low end damage of all abilities as a function of
        specified boss debuffs."""
        bonus_damage = (
            self.attack_power/14 + 8 * gift_of_arthas + self.bonus_damage
            + 40 * tigers_fury
        )
        residual_armor = max(0, (
            boss_armor - max(sunder * 2600, imp_EA * 3075) - 800 * CoR
            - 610 * faerie_fire - 600 * annihilator - self.armor_pen
        ))
        armor_multiplier = (
            1 - residual_armor / (residual_armor - 22167.5 + 467.5*70)
        )
        damage_multiplier = self.damage_multiplier * (1 + 0.04 * blood_frenzy)
        self.multiplier = armor_multiplier * damage_multiplier
        self.white_low = (43.5 + bonus_damage) * self.multiplier
        self.white_high = (66.5 + bonus_damage) * self.multiplier
        self.shred_low = (
            self.white_low * 2.25 + (405 + self.shred_bonus) * self.multiplier
        )
        self.shred_high = (
            self.white_high * 2.25 + (405 + self.shred_bonus) * self.multiplier
        )
        self.bite_multiplier = self.multiplier * (1+0.03*self.feral_aggression)
        self.bite_low = {
            5: (935 + 0.25 * self.attack_power) * self.bite_multiplier,
            4: (766 + 0.2 * self.attack_power) * self.bite_multiplier
        }
        self.bite_high = {
            5: (968 + 0.25 * self.attack_power) * self.bite_multiplier,
            4: (799 + 0.2 * self.attack_power) * self.bite_multiplier
        }
        mangle_fac = 1 + 0.1 * self.savage_fury
        self.claw_low = mangle_fac * (self.white_low + 190 * self.multiplier)
        self.claw_high = mangle_fac * (self.white_high + 190 * self.multiplier)
        self.mangle_low = mangle_fac * (
            self.white_low * 1.6 + 264 * self.multiplier
        )
        self.mangle_high = mangle_fac * (
            self.white_high * 1.6 + 264 * self.multiplier
        )
        self.rip_tick = {
            5: (1092 + 0.24*self.attack_power) / 6 * damage_multiplier,
            4: (894 + 0.24*self.attack_power) / 6 * damage_multiplier
        }

    def reset(self):
        """Reset fight-specific parameters to their starting values at the
        beginning of an encounter."""
        self.gcd = 0.0
        self.omen_proc = False
        self.omen_icd = 0.0
        self.energy = 100
        self.combo_points = 0
        self.mana = self.mana_pool
        self.rune_cd = 0.0
        self.pot_cd = 0.0
        self.pot_active = False
        self.innervated = False
        self.innervate_cd = 0.0
        self.five_second_rule = False
        self.cat_form = True
        self.t4_proc = False

        # Create dictionary to hold breakdown of total casts and damage
        self.dmg_breakdown = collections.OrderedDict()

        for cast_type in [
            'Melee', 'Mangle', 'Shred', 'Rip', 'Claw', 'Ferocious Bite',
            'Shift'
        ]:
            self.dmg_breakdown[cast_type] = {'casts': 0, 'damage': 0.0}

    def check_omen_proc(self, yellow=False):
        """Check for Omen of Clarity proc on a successful swing.

        Arguments:
            yellow (bool): Check proc for a yellow ability rather than a melee
                swing. Defaults False.
        """
        if not self.omen:
            return
        if self.omen_icd > 1e-9:
            return

        if yellow:
            proc_rate = self.omen_rates['yellow']
        else:
            proc_rate = self.omen_rates['white']

        proc_roll = np.random.rand()

        if proc_roll < proc_rate:
            self.omen_proc = True
            self.omen_icd = 10.0

    def check_jow_proc(self):
        """Check for a Judgment Wisdom on a successful melee attack."""
        if not self.jow:
            return

        proc_roll = np.random.rand()

        if proc_roll < 0.5:
            self.mana = min(self.mana + 74, self.mana_pool)

    def check_t4_proc(self):
        """Check for a 2p-T4 energy proc on a successful melee attack."""
        self.t4_proc = False

        if not self.t4_bonus:
            return

        proc_roll = np.random.rand()

        if proc_roll < 0.04:
            self.energy = min(self.energy + 20, 100)
            self.t4_proc = True

    def regen_mana(self, pot=False):
        """Update player mana on a Spirit tick.

        Arguments:
            pot (bool): Whether the mana regeneration comes from a Fel Mana
                Potion tick rather than a conventional spirit tick. Defaults
                False.
        """
        if pot:
            regen = 400
        elif self.innervated:
            regen = self.regen_rates['innervated']
        elif self.five_second_rule:
            regen = self.regen_rates['five_second_rule']
        else:
            regen = self.regen_rates['base']

        self.mana = min(self.mana + regen, self.mana_pool)

    def use_rune(self):
        """Pop a Dark/Demonic Rune to restore mana when appropriate.

        Returns:
            rune_used (bool): Whether the rune was used.
        """
        if ((not self.rune) or (self.rune_cd > 1e-9)
                or (self.mana > self.mana_pool - 1500)):
            return False

        self.mana += (900 + np.random.rand() * 600)
        self.rune_cd = 120.0
        return True

    def use_pot(self, time):
        """Pop a Mana Potion to restore mana when appropriate.

        Arguments:
            time (float): Time at which the potion is consumed. Used to
                generate a list of tick times for Fel Mana regen.

        Returns:
            pot_used (bool): Wheter the potion was used.
        """
        if ((not self.pot) or (self.pot_cd > 1e-9)
                or (self.mana > self.pot_threshold)):
            return False

        self.pot_cd = 120.0

        # If we're using cheap potions, we ignore the Fel Mana tick logic
        if self.cheap_pot:
            self.mana += (1800 + np.random.rand() * 1200)
        else:
            self.pot_active = True
            self.pot_ticks = list(np.arange(time + 3, time + 24.01, 3))
            self.pot_end = time + 24

        return True

    def swing(self):
        """Execute a melee swing.

        Returns:
            damage_done (float): Damage done by the swing.
        """
        damage_done, miss, crit = calc_white_damage(
            self.white_low, self.white_high, self.miss_chance, self.crit_chance
        )

        # Check for Omen and JoW procs
        if not miss:
            self.check_omen_proc()
            self.check_jow_proc()
            self.check_t4_proc()

        # Log the swing
        self.dmg_breakdown['Melee']['casts'] += 1
        self.dmg_breakdown['Melee']['damage'] += damage_done

        if self.log:
            self.gen_log('melee', damage_done, miss, crit, False)

        return damage_done

    def gen_log(self, ability_name, dmg_done, miss, crit, clearcast):
        """Generate a combat log entry for an ability.

        Arguments:
            ability_name (str): Name of the ability.
            dmg_done (float): Damage done by the ability.
            miss (bool): Whether the ability missed.
            crit (bool): Whether the ability crit.
            clearcast (bool): Whether the ability was a Clearcast.
        """
        if miss:
            damage_str = 'miss' + ' (clearcast)' * clearcast
        else:
            try:
                damage_str = '%d' % dmg_done
            except TypeError:
                damage_str = dmg_done

            if crit and clearcast:
                damage_str += ' (crit, clearcast)'
            elif crit:
                damage_str += ' (crit)'
            elif clearcast:
                damage_str += ' (clearcast)'

            if self.t4_proc:
                if ')' in damage_str:
                    damage_str = damage_str[:-1] + ', T4 proc)'
                else:
                    damage_str += ' (T4 proc)'

        self.combat_log = [
            ability_name, damage_str, '%d' % self.energy,
            '%d' % self.combo_points, '%d' % self.mana
        ]

    def execute_builder(
        self, ability_name, min_dmg, max_dmg, energy_cost, mangle_mod=False
    ):
        """Execute a combo point builder (either Claw, Shred, or Mangle).

        Arguments:
            ability_name (str): Name of the ability for use in logging.
            min_dmg (float): Low end damage of the ability.
            max_dmg (float): High end damage of the ability.
            energy_cost (int): Energy cost of the ability.
            mangle_mod (bool): Whether to apply the Mangle damage modifier to
                the ability. Defaults False.

        Returns:
            damage_done (float): Damage done by the ability.
            success (float): Whether the ability successfully landed.
        """
        # Perform Monte Carlo
        damage_done, miss, crit = calc_yellow_damage(
            min_dmg, max_dmg, self.miss_chance, self.crit_chance
        )

        if mangle_mod:
            damage_done *= 1.3

        # Set GCD
        self.gcd = 1.0

        # Update energy
        clearcast = self.omen_proc

        if clearcast:
            self.omen_proc = False
        else:
            self.energy -= energy_cost * (1 - 0.8 * miss)

        # Update combo points
        points_added = 1 * (not miss) + crit
        self.combo_points = min(5, self.combo_points + points_added)

        # Check for Omen and JoW procs
        if not miss:
            self.check_omen_proc(yellow=True)
            self.check_jow_proc()
            self.check_t4_proc()

        # Log the cast
        self.dmg_breakdown[ability_name]['casts'] += 1
        self.dmg_breakdown[ability_name]['damage'] += damage_done

        if self.log:
            self.gen_log(ability_name, damage_done, miss, crit, clearcast)

        return damage_done, not miss

    def shred(self):
        """Execute a Shred.

        Returns:
            damage_done (float): Damage done by the Shred cast.
        """
        damage_done, _ = self.execute_builder(
            'Shred', self.shred_low, self.shred_high, 42, mangle_mod=True
        )
        return damage_done

    def claw(self):
        """Execute a Claw.

        Returns:
            damage_done (float): Damage done by the Claw cast.
        """
        damage_done, _ = self.execute_builder(
            'Claw', self.claw_low, self.claw_high, 40
        )
        return damage_done

    def mangle(self):
        """Execute a Mangle.

        Returns:
            damage_done (float): Damage done by the Mangle cast.
            success (bool): Whether the Mangle debuff was successfully applied.
        """
        return self.execute_builder(
            'Mangle', self.mangle_low, self.mangle_high, 40
        )

    def bite(self):
        """Execute a Ferocious Bite.

        Returns:
            damage_done (float): Damage done by the Bite cast.
        """
        # Bite always costs at least 35 combo points without Omen of Clarity
        clearcast = self.omen_proc

        if clearcast:
            self.omen_proc = False
        else:
            self.energy -= 35

        # Update Bite damage based on excess energy available
        bonus_damage = self.energy * 4.1 * self.bite_multiplier

        # Perform Monte Carlo
        damage_done, miss, crit = calc_yellow_damage(
            self.bite_low[self.combo_points] + bonus_damage,
            self.bite_high[self.combo_points] + bonus_damage, self.miss_chance,
            self.crit_chance
        )

        # Consume energy pool and combo points on successful Bite
        self.energy *= miss
        self.combo_points *= miss

        # Set GCD
        self.gcd = 1.0

        # Check for Omen and JoW procs
        if not miss:
            self.check_omen_proc(yellow=True)
            self.check_jow_proc()
            self.check_t4_proc()

        # Log the cast
        self.dmg_breakdown['Ferocious Bite']['casts'] += 1
        self.dmg_breakdown['Ferocious Bite']['damage'] += damage_done

        if self.log:
            self.gen_log('Ferocious Bite', damage_done, miss, crit, clearcast)

        return damage_done

    def rip(self):
        """Cast Rip as a finishing move.

        Returns:
            damage_per_tick (float): Damage done per subsequent Rip tick.
            success (bool): Whether the Rip debuff was successfully applied.
        """
        # Perform Monte Carlo to see if it landed and record damage per tick
        miss = (np.random.rand() < self.miss_chance)
        damage_per_tick = self.rip_tick[self.combo_points] * (not miss)

        # Set GCD
        self.gcd = 1.0

        # Update energy
        clearcast = self.omen_proc

        if clearcast:
            self.omen_proc = False
        else:
            self.energy -= 30

        # Consume combo points on successful cast
        self.combo_points *= miss

        # Check for Omen and JoW procs
        if not miss:
            self.check_omen_proc(yellow=True)
            self.check_jow_proc()
            self.check_t4_proc()

        # Log the cast and total damage that will be done
        self.dmg_breakdown['Rip']['casts'] += 1
        self.dmg_breakdown['Rip']['damage'] += damage_per_tick * 6

        if self.log:
            self.gen_log('Rip', 'applied', miss, False, clearcast)

        return damage_per_tick, not miss

    def shift(self, time):
        """Execute a powershift.

        Arguments:
            time (float): Time at which the shift is executed, in seconds. Used
                for determining the five second rule.
        """
        self.energy = 60
        self.gcd = 1.5
        self.dmg_breakdown['Shift']['casts'] += 1
        self.mana -= self.shift_cost
        self.five_second_rule = True
        self.last_cast_time = time
        self.cat_form = True
        mana_str = ''

        # Pop a Dark Rune if we can get full value from it
        if self.use_rune():
            mana_str = 'use Dark Rune'

        # Pop a Mana Potion if we can get full value from it
        if self.use_pot(time):
            mana_str = 'use Mana Potion'

        if self.log:
            self.combat_log = [
                'shift', mana_str, '%d' % self.energy,
                '%d' % self.combo_points, '%d' % self.mana
            ]

    def innervate(self, time):
        """Cast Innervate.

        Arguments:
            time (float): Time of Innervate cast, in seconds. Used for
                determining when the Innervate buff falls off.
        """
        self.mana -= 95  # Innervate mana cost
        self.innervate_end = time + 20
        self.innervated = True
        self.cat_form = False
        self.energy = 0
        self.gcd = 1.5
        self.innervate_cd = 360.0

        if self.log:
            self.combat_log = [
                'Innervate', '', '%d' % self.energy,
                '%d' % self.combo_points, '%d' % self.mana
            ]


class Simulation():

    """Sets up and runs a simulated fight with the cat DPS rotation."""

    # Default fight parameters, including boss armor and all relevant debuffs.
    default_params = {
        'gift_of_arthas': True,
        'boss_armor': 3731,
        'sunder': False,
        'imp_EA': True,
        'CoR': True,
        'faerie_fire': True,
        'annihilator': False,
        'blood_frenzy': False
    }

    # Default parameters specifying the player execution strategy
    default_strategy = {
        'prepop_TF': False,
        'prepop_numticks': 2,
        'min_combos_for_rip': 4,
        'use_innervate': True
    }

    def __init__(self, player, fight_length, num_mcp=0, **kwargs):
        """Initialize simulation.

        Arguments:
            player (Player): An instantiated Player object which can execute
                the DPS rotation.
            fight_length (float): Fight length in seconds.
            num_mcp (int): Maximum number of MCPs that can be used during the
                fight. If nonzero, the Player object should be instantiated
                with a hasted swing timer, and the simulation will slow it down
                once the haste buff expires. Defaults to 0.
            kwargs (dict): Key, value pairs for all other encounter parameters,
                including boss armor, relevant debuffs, and player stregy
                specification. An error will be thrown if the parameter is not
                recognized. Any parameters not supplied will be set to default
                values.
        """
        self.player = player
        self.fight_length = fight_length
        self.max_mcp = int(round(num_mcp))
        self.params = copy.deepcopy(self.default_params)
        self.strategy = copy.deepcopy(self.default_strategy)

        for key, value in kwargs.items():
            if key in self.params:
                self.params[key] = value
            elif key in self.strategy:
                self.strategy[key] = value
            else:
                raise KeyError(
                    ('"%s" is not a supported parameter. Supported encounter '
                     'parameters are: %s. Supported strategy parameters are: '
                     '%s.') % (key, self.params.keys(), self.strategy.keys())
                )

        # Calculate damage ranges for player abilities under the given
        # encounter parameters.
        self.player.calc_damage_params(**self.params)

    def set_active_debuffs(self, debuff_list):
        """Set active debuffs according to a specified list.

        Arguments:
            debuff_list (list): List of strings containing supported debuff
                names.
        """
        active_debuffs = copy.copy(debuff_list)
        all_debuffs = [key for key in self.params if key != 'boss_armor']

        for key in all_debuffs:
            if key in active_debuffs:
                self.params[key] = True
                active_debuffs.remove(key)
            else:
                self.params[key] = False

        if active_debuffs:
            raise ValueError(
                'Unsupported debuffs found: %s. Supported debuffs are: %s.' % (
                    active_debuffs, self.params.keys()
                )
            )

    def gen_log(self, time, event, outcome):
        """Generate a custom combat log entry.

        Arguments:
            time (float): Current simulation time in seconds.
            event (str): First "event" field for the log entry.
            outcome (str): Second "outcome" field for the log entry.
        """
        return [
            '%.3f' % time, event, outcome, '%d' % self.player.energy,
            '%d' % self.player.combo_points, '%d' % self.player.mana
        ]

    def innervate_or_shift(self, time):
        """Decide whether to cast Innervate or perform a normal powershift.

        Arguments:
            time (float): Current simulation time in seconds.
        """
        # Only Innervate if (a) we don't have enough mana for two shifts, (b)
        # the fight isn't ending, and (c) Innervate is not on cooldown.
        if (self.strategy['use_innervate']
                and (self.player.mana <= self.innervate_threshold)
                and (time < self.fight_length - 1.6)
                and (self.player.innervate_cd < 1e-9)):
            # First execute the Innervate cast. Player object will track the
            # time of cast.
            self.player.innervate(time)

            # Next we need to reset the melee swing timer since we're staying
            # in caster form. We'll use the same logic as at the start of
            # combat, setting the first swing just slightly after the shift
            # back into cat.
            self.update_swing_times(time + 1.5 + 0.1 * np.random.rand())
        else:
            self.player.shift(time)

        # If needed, squeeze in a weapon swap into the same GCD
        if (not self.mcp_equipped) and (self.num_mcp >= 1):
            self.mcp_equipped = True
            self.mcp_cd = 30.0
            self.num_mcp -= 1

    def mangle(self, time):
        """Instruct the Player to Mangle, and perform related bookkeeping.

        Arguments:
            time (float): Current simulation time in seconds.

        Returns:
            damage_done (float): Damage done by the Mangle cast.
        """
        damage_done, success = self.player.mangle()

        # If it landed, flag the debuff as active and start timer
        if success:
            self.mangle_debuff = True
            self.mangle_end = time + 12.0

        return damage_done

    def rip(self, time):
        """Instruct Player to apply Rip, and perform related bookkeeping.

        Arguments:
            time (float): Current simulation time in seconds.
        """
        damage_per_tick, success = self.player.rip()

        if success:
            self.rip_debuff = True
            self.rip_end = time + 12.0
            self.rip_ticks = list(np.arange(time + 2, time + 12.01, 2))
            self.rip_damage = damage_per_tick

    def execute_rotation(self, time, next_tick):
        """Execute the next player action in the DPS rotation according to the
        specified player strategy in the simulation.

        Arguments:
            time (float): Current simulation time in seconds.
            next_tick (float): Time of next energy tick, in seconds.

        Returns:
            damage_done (float): Damage done by the player action.
        """
        # If we're out of form because we just cast Innervate, always shift
        if not self.player.cat_form:
            self.player.shift(time)
            return 0.0

        energy, cp = self.player.energy, self.player.combo_points
        rip_cp = self.strategy['min_combos_for_rip']
        rip_now = (cp >= rip_cp) and (not self.rip_debuff)
        mangle_now = (not rip_now) and (not self.mangle_debuff)
        rip_next = (
            rip_now or ((cp >= rip_cp) and (self.rip_end <= next_tick))
        )
        mangle_next = (
            (not rip_next) and (mangle_now or (self.mangle_end <= next_tick))
        )

        if self.player.mana < self.player.shift_cost:
            # If this is the first time we're oom, log it
            if self.time_to_oom is None:
                self.time_to_oom = time

            # No-shift rotation
            if (rip_now and ((energy >= 30) or self.player.omen_proc)):
                self.rip(time)
            elif (mangle_now and ((energy >= 40) or self.player.omen_proc)):
                return self.mangle(time)
            elif (energy >= 42) or self.player.omen_proc:
                return self.player.shred()
        elif energy < 10:
            self.innervate_or_shift(time)
        elif rip_now:
            if (energy >= 30) or self.player.omen_proc:
                self.rip(time)
        elif mangle_now:
            if (energy < 20) and (not rip_next):
                self.innervate_or_shift(time)
            elif (energy >= 40) or self.player.omen_proc:
                return self.mangle(time)
        elif energy >= 22:
            if (energy >= 42) or self.player.omen_proc:
                return self.player.shred()
        elif (not rip_next) and ((energy < 20) or (not mangle_next)):
            self.innervate_or_shift(time)

        return 0.0

    def update_swing_times(self, start_time):
        """Generate an updated list of swing times after changes to the swing
        timer have occurred.

        Arguments:
            start_time (float): Time of first swing, in seconds.
        """
        if start_time > self.fight_length - self.swing_timer:
            self.swing_times = [
                start_time, start_time + self.swing_timer
            ]
        else:
            self.swing_times = list(np.arange(
                start_time, self.fight_length + self.swing_timer,
                self.swing_timer
            ))

    def drop_tigers_fury(self, time):
        """Remove Tiger's Fury buff and document if requested.

        Arguments:
            time (float): Simulation time when Tiger's Fury fell off, in
                seconds. Required only if log_event is True.
        """
        self.player.calc_damage_params(tigers_fury=False, **self.params)

        if self.log:
            self.combat_log.append(
                self.gen_log(time, "Tiger's Fury", 'falls off')
            )

    def run(self, log=False):
        """Run a simulated trajectory for the fight.

        Arguments:
            log (bool): If True, generate a full combat log of events within
                the simulation. Defaults False.

        Returns:
            times, damage, energy, combos: Lists of the time,
                total damage done, player energy, and player combo points at
                each simulated event within the fight duration.
            damage_breakdown (collection.OrderedDict): Dictionary containing a
                breakdown of the number of casts and damage done by each player
                ability.
            combat_log (list of lists): Each entry is a list [time, event,
                outcome, energy, combo points, mana] all formatted as strings.
                Only output if log == True.
        """
        # Reset player to fresh fight
        self.player.reset()
        self.innervate_threshold = 2 * self.player.shift_cost + 95
        self.mangle_debuff = False
        self.rip_debuff = False

        # Configure combat logging if requested
        self.log = log

        if self.log:
            self.player.log = True
            self.combat_log = []
        else:
            self.player.log = False

        # Fight begins at a random time relative to energy tick. Since we start
        # at 100 energy, let's random roll the time of the next tick.
        energy_tick_start = 2.0 * np.random.rand()

        # Create array of energy tick times
        energy_tick_times = list(np.arange(
            energy_tick_start, self.fight_length + 2, 2
        ))

        # Same thing for swing times, except that the first swing will occur at
        # most 100 ms after the first special just to simulate some latency and
        # avoid errors from Omen procs on the first swing.
        self.swing_timer = self.player.swing_timer
        swing_timer_start = 0.1 * np.random.rand()
        self.update_swing_times(swing_timer_start)

        # Adjust damage calculation if Tiger's Fury is pre-popped, and
        # calculate when it should fall off for the specified strategy. Assume
        # TF is popped 100 ms before the appropriate energy tick.
        if self.strategy['prepop_TF']:
            self.player.calc_damage_params(tigers_fury=True, **self.params)
            tf_end = (
                energy_tick_start - 0.1 + 6
                - 2 * self.strategy['prepop_numticks']
            )
            self.player.energy -= 10 * (2 - self.strategy['prepop_numticks'])
            tf_active = True
        else:
            tf_active = False

        # Determine whether MCP will be used, and activate it if so
        self.num_mcp = self.max_mcp

        if self.num_mcp >= 1:
            self.mcp_equipped = True
            mcp_active = True
            mcp_end = 90.0
            self.num_mcp -= 1
            self.mcp_cd = 0.0
        else:
            self.mcp_equipped = False

        # Create placeholder for time to OOM if the player goes OOM in the run
        self.time_to_oom = None

        # Create empty lists of output variables
        times = []
        damage = []
        energy = []
        combos = []

        # The "damage_done" for Rip that is logged by the Player object is not
        # accurate to a given run, as it does not incorporate the Mangle
        # debuff or partial Rip ticks at the end. So we'll keep track of it
        # ourselves.
        rip_damage = 0.0

        # Run simulation
        time = 0.0
        previous_time = 0.0

        while time <= self.fight_length:
            # Tabulate all damage sources in this timestep
            dmg_done = 0.0

            # Decrement cooldowns by time since last event
            delta_t = time - previous_time
            self.player.gcd = max(0.0, self.player.gcd - delta_t)
            self.player.omen_icd = max(0.0, self.player.omen_icd - delta_t)
            self.player.rune_cd = max(0.0, self.player.rune_cd - delta_t)
            self.player.pot_cd = max(0.0, self.player.pot_cd - delta_t)
            self.player.innervate_cd = max(
                0.0, self.player.innervate_cd - delta_t
            )

            if self.mcp_equipped:
                self.mcp_cd = max(0.0, self.mcp_cd - delta_t)

            if (self.player.five_second_rule
                    and (time - self.player.last_cast_time >= 5)):
                self.player.five_second_rule = False

            # Check if Innervate fell off
            if self.player.innervated and (time >= self.player.innervate_end):
                self.player.innervated = False

                if self.log:
                    self.combat_log.append(self.gen_log(
                        self.player.innervate_end, 'Innervate', 'falls off'
                    ))

            # Check if Tiger's Fury fell off
            if tf_active and (time >= tf_end):
                self.drop_tigers_fury(tf_end)
                tf_active = False

            # Check if haste buff is expired or if a new one can be popped
            if self.mcp_equipped and mcp_active and (time >= mcp_end):
                mcp_active = False
                self.mcp_equipped = False
                self.swing_timer = calc_swing_timer(
                    calc_haste_rating(self.swing_timer) - 500
                )
                self.update_swing_times(self.swing_times[0])

                if self.log:
                    self.combat_log.append(self.gen_log(
                        mcp_end, 'Haste', 'falls off'
                    ))
            elif self.mcp_equipped and (not mcp_active) and (self.mcp_cd == 0):
                mcp_active = True
                self.swing_timer = calc_swing_timer(
                    calc_haste_rating(self.swing_timer) + 500
                )
                self.update_swing_times(self.swing_times[0])
                mcp_end = time + 90.0

                if self.log:
                    self.combat_log.append(
                        self.gen_log(time, 'Haste', 'applied')
                    )

            # Check if Mangle fell off
            if self.mangle_debuff and (time >= self.mangle_end):
                self.mangle_debuff = False

                if self.log:
                    self.combat_log.append(
                        self.gen_log(self.mangle_end, 'Mangle', 'falls off')
                    )

            # Check if a Rip tick happens at this time
            if self.rip_debuff and (time == self.rip_ticks[0]):
                tick_damage = self.rip_damage * (1 + 0.3 * self.mangle_debuff)
                dmg_done += tick_damage
                rip_damage += tick_damage
                self.rip_ticks.pop(0)

                if self.log:
                    self.combat_log.append(
                        self.gen_log(time, 'Rip tick', '%d' % tick_damage)
                    )

            # Check if Rip fell off
            if self.rip_debuff and (time > self.rip_end - 1e-9):
                self.rip_debuff = False

                if self.log:
                    self.combat_log.append(
                        self.gen_log(self.rip_end, 'Rip', 'falls off')
                    )

            # Check if a melee swing happens at this time
            if time == self.swing_times[0]:
                dmg_done += self.player.swing()
                self.swing_times.pop(0)

                if self.log:
                    self.combat_log.append(
                        ['%.3f' % time] + self.player.combat_log
                    )

            # Check if an energy/spirit tick happens at this time
            if time == energy_tick_times[0]:
                self.player.energy = (
                    min(100, self.player.energy + 20) * self.player.cat_form
                )
                self.player.regen_mana()
                energy_tick_times.pop(0)

                if self.log:
                    self.combat_log.append(
                        self.gen_log(time, 'energy tick', '')
                    )

            # Check if a Fel Mana Potion tick happens at this time
            if self.player.pot_active and (time == self.player.pot_ticks[0]):
                self.player.regen_mana(pot=True)
                self.player.pot_ticks.pop(0)

                if self.log:
                    self.combat_log.append(
                        self.gen_log(time, 'Fel Mana tick', '')
                    )

            # Check if Fel Mana Potion expired
            if self.player.pot_active and (time > self.player.pot_end - 1e-9):
                self.player.pot_active = False

                if self.log:
                    self.combat_log.append(self.gen_log(
                        self.player.pot_end, 'Fel Mana', 'falls off'
                    ))

            # Determine next energy tick
            next_tick = energy_tick_times[0]

            # Check if we're able to act, and if so execute the optimal cast.
            self.player.combat_log = None

            if self.player.gcd < 1e-9:
                dmg_done += self.execute_rotation(time, next_tick)

            # Log current parameters
            times.append(time)
            damage.append(dmg_done)
            energy.append(self.player.energy)
            combos.append(self.player.combo_points)

            if self.log and self.player.combat_log:
                self.combat_log.append(
                    ['%.3f' % time] + self.player.combat_log
                )

            # If we entered caster form, Tiger's Fury fell off
            if tf_active and (self.player.gcd == 1.5):
                self.drop_tigers_fury(time)
                tf_active = False

            # Update time
            previous_time = time
            next_swing = self.swing_times[0]

            if self.player.gcd > 1e-9:
                time = min(time + self.player.gcd, next_swing, next_tick)
            else:
                time = min(next_swing, next_tick)

            if self.rip_debuff:
                time = min(time, self.rip_ticks[0])
            if self.player.pot_active:
                time = min(time, self.player.pot_ticks[0])

        # Replace logged Rip damgae with the actual value realized in the run
        self.player.dmg_breakdown['Rip']['damage'] = rip_damage
        output = (times, damage, energy, combos, self.player.dmg_breakdown)

        if self.log:
            output += (self.combat_log,)

        return output

    def run_replicates(self, num_replicates, detailed_output=False):
        """Perform several runs of the simulation in order to collect
        statistics on performance.

        Arguments:
            num_replicates (int): Number of replicates to run.
            detailed_output (bool): Whether to consolidate details about cast
                and mana statistics in addition to DPS values. Defaults False.

        Returns:
            dps_vals (np.ndarray): Array containing average DPS of each run.
            cast_summary (collections.OrderedDict): Dictionary containing
                averaged statistics for the number of casts and total damage
                done by each player ability over the simulated fight length.
                Output only if detailed_output == True.
            oom_times (np.ndarray): Array containing times at which the player
                went oom in each run. Output only if detailed_output == True.
                If the player did not oom in a run, the corresponding entry
                will be the total fight length.
        """
        # Make sure damage and mana parameters are up to date
        self.player.calc_damage_params(**self.params)
        self.player.set_mana_regen()

        # Run replicates and consolidate results
        dps_vals = np.zeros(num_replicates)

        if detailed_output:
            oom_times = np.zeros(num_replicates)

        for i in range(num_replicates):
            # Randomize fight length to avoid haste clipping effects. We will
            # use a normal distribution centered around the target length, with
            # a standard deviation of 1 second (unhasted swing timer). Impact
            # of the choice of distribution needs to be assessed...
            base_fight_length = self.fight_length
            randomized_fight_length = base_fight_length + np.random.randn()
            self.fight_length = randomized_fight_length
            _, damage, _, _, dmg_breakdown = self.run()
            avg_dps = np.sum(damage) / self.fight_length
            dps_vals[i] = avg_dps
            self.fight_length = base_fight_length

            if not detailed_output:
                continue

            # Consolidate damage breakdown for the fight
            if i == 0:
                cast_sum = copy.deepcopy(dmg_breakdown)
            else:
                for ability in cast_sum:
                    for key in cast_sum[ability]:
                        val = dmg_breakdown[ability][key]
                        cast_sum[ability][key] = (
                            (cast_sum[ability][key] * i + val) / (i + 1)
                        )

            # Consolidate oom time
            if self.time_to_oom is None:
                oom_times[i] = randomized_fight_length
            else:
                oom_times[i] = self.time_to_oom

        if not detailed_output:
            return dps_vals

        return dps_vals, cast_sum, oom_times

    def calc_deriv(self, num_replicates, param, increment, base_dps):
        """Calculate DPS increase after incrementing a player stat.

        Arguments:
            num_replicates (int): Number of replicates to run.
            param (str): Player attribute to increment.
            increment (float): Magnitude of stat increment.
            base_dps (float): Pre-calculated base DPS before stat increments.

        Returns:
            dps_delta (float): Average DPS increase after the stat increment.
                The Player attribute will be reset to its original value once
                the calculation is finished.
        """
        # Increment the stat
        original_value = getattr(self.player, param)
        setattr(self.player, param, original_value + increment)

        # Calculate DPS
        dps_vals = self.run_replicates(num_replicates)
        avg_dps = np.mean(dps_vals)

        # Reset the stat to original value
        setattr(self.player, param, original_value)
        return avg_dps - base_dps

    def calc_stat_weights(
            self, num_replicates, base_dps=None, unleashed_rage=False
    ):
        """Calculate performance derivatives for AP, hit, crit, and haste.

        Arguments:
            num_replicates (int): Number of replicates to run.
            base_dps (float): If provided, use a pre-calculated value for the
                base DPS before stat increments. Defaults to calculating base
                DPS from scratch.
            unleashed_rage (bool): Whether the Unleashed Rage party buff should
                be factored into the computed AP weight. Defaults False.

        Returns:
            dps_deltas (dict): Dictionary containing DPS increase from 1 AP,
                1% hit, 1% crit, and 1% haste.
            stat_weights (dict): Dictionary containing normalized stat weights
                for 1% hit, 1% crit, and 1% haste relative to 1 AP.
        """
        # First store base DPS and deltas after each stat increment
        dps_deltas = {}

        if base_dps is None:
            dps_vals = self.run_replicates(num_replicates)
            base_dps = np.mean(dps_vals)

        # For all stats, we will use a much larger increment than +1 in order 
        # to see sufficient DPS increases above the simulation noise. We will
        # then linearize the increase down to a +1 increment for weight
        # calculation. This approximation is accurate as long as DPS is linear
        # in each stat up to the larger increment that was used.

        # For AP, we will use an increment of +80 AP. We also scale the
        # increase by a factor of 1.1 to account for HotW
        ap_mod = 1.1 * (1 + 0.1 * unleashed_rage)
        dps_deltas['1 AP'] = ap_mod * 1.0/80.0 * self.calc_deriv(
            num_replicates, 'attack_power', 80, base_dps
        )

        # For hit and crit, we will use an increment of 2%.

        # For hit, we reduce miss chance by 2% if well below hit cap, and
        # increase miss chance by 2% when already capped or close.
        sign = 1 - 2 * int(self.player.miss_chance < 0.085)
        dps_deltas['1% hit'] = 0.5 * sign * self.calc_deriv(
            num_replicates, 'miss_chance', -sign * 0.02, base_dps
        )

        # Crit is a simple increment
        dps_deltas['1% crit'] = 0.5 * self.calc_deriv(
            num_replicates, 'crit_chance', 0.02, base_dps
        )

        # For haste we will use an increment of 4%. (Note that this is 4% in
        # one slot and not four individual 1% buffs.) We implement the
        # increment by reducing the player swing timer.
        base_haste_rating = calc_haste_rating(self.player.swing_timer)
        swing_delta = (
            self.player.swing_timer -
            calc_swing_timer(base_haste_rating + 63.08)
        )
        dps_deltas['1% haste'] = 0.25 * self.calc_deriv(
            num_replicates, 'swing_timer', -swing_delta, base_dps
        )

        # For armor pen, we use an increment of 300.
        dps_deltas['1 Armor Pen'] = 1./300. * self.calc_deriv(
            num_replicates, 'armor_pen', 300, base_dps
        )

        # For weapon damage, we use an increment of 12
        dps_deltas['1 Weapon Damage'] = 1./12. * self.calc_deriv(
            num_replicates, 'bonus_damage', 12, base_dps
        )

        # Calculate normalized stat weights
        stat_weights = {}

        for stat in dps_deltas:
            if stat != '1 AP':
                stat_weights[stat] = dps_deltas[stat] / dps_deltas['1 AP']

        return dps_deltas, stat_weights

    def calc_mana_weights(self, num_replicates, base_dps, dps_per_AP):
        """Calculate weights for mana stats in situations where the player goes
        oom before the end of the fight. It is assumed that the regular stat
        weights have already been calculated prior to calling this method.

        Arguments:
            num_replicates (int): Number of replicates to run.
            base_dps (float): Average base DPS before stat increments.
            dps_per_AP (float): DPS added by 1 AP. This is output by the
                calc_stat_weights() method, and is used to normalize the mana
                weights.

        Returns:
            dps_deltas (dict): Dictionary containing DPS increase from 1 Int,
                1 Spirit, and 1 mp5. Int and Spirit contributions are not
                boosted by ZG buff or Blessing of Kings, and should be adjusted
                accordingly.
            stat_weights (dict): Dictionary containing normalized stat weights
                for 1 Int, 1 Spirit, and 1 mp5 relative to 1 AP.
        """
        dps_deltas = {}

        # For mana weight, increment player mana pool by one shift's worth
        dps_deltas['1 mana'] = 1.0 / self.player.shift_cost * self.calc_deriv(
            num_replicates, 'mana_pool', self.player.shift_cost, base_dps
        )

        # For spirit weight, calculate how much spirit regens an additional 
        # full shift's worth of mana over the course of Innervate.
        base_regen_delta = self.player.shift_cost / 10 / 5
        spirit_delta = base_regen_delta / self.player.regen_factor
        dps_deltas['1 Spirit'] = 1.0 / spirit_delta * self.calc_deriv(
            num_replicates, 'spirit', spirit_delta, base_dps
        )

        # Combine mana and regen contributions of Int
        mana_contribution = 15 * dps_deltas['1 mana']
        spirit_contribution = (
            self.player.spirit / (2 * self.player.intellect)
            * dps_deltas['1 Spirit']
        )
        dps_deltas['1 Int'] = mana_contribution + spirit_contribution

        # Same thing for mp5, except we integrate over the full fight length
        delta_mp5 = np.ceil(self.player.shift_cost / (self.fight_length / 5))
        dps_deltas['1 mp5'] = 1.0 / delta_mp5 * self.calc_deriv(
            num_replicates, 'mp5', delta_mp5, base_dps
        )

        # Calculate normalized stat weights
        stat_weights = {}

        for stat in ['1 mana', '1 Spirit', '1 Int', '1 mp5']:
            stat_weights[stat] = dps_deltas[stat] / dps_per_AP

        return dps_deltas, stat_weights
