"""Code for modeling non-static trinkets in feral DPS simulation."""

import numpy as np


class Trinket():

    """Keeps track of activation times and cooldowns for an equipped trinket,
    updates Player and Simulation parameters when the trinket is active, and
    determines when procs or trinket activations occur."""

    def __init__(
        self, stat_name, stat_increment, proc_name, proc_duration, cooldown
    ):
        """Initialize a generic trinket with key parameters.

        Arguments:
            stat_name (str): Name of the Player attribute that will be
                modified by the trinket activation. Must be a valid attribute
                of the Player class that can be modified. The one exception is
                haste_rating, which is separately handled by the Simulation
                object when updating timesteps for the sim.
            stat_increment (float): Amount by which the Player attribute is
                changed when the trinket is active.
            proc_name (str): Name of the buff that is applied when the trinket
                is active. Used for combat logging.
            proc_duration (int): Duration of the buff, in seconds.
            cooldown (int): Internal cooldown before the trinket can be
                activated again, either via player use or procs.
        """
        self.stat_name = stat_name
        self.stat_increment = stat_increment
        self.proc_name = proc_name
        self.proc_duration = proc_duration
        self.cooldown = cooldown
        self.reset()

    def reset(self):
        """Set trinket to fresh inactive state with no cooldown remaining."""
        self.activation_time = -np.inf
        self.active = False
        self.can_proc = True

    def modify_stat(self, time, player, sim, increment):
        """Change a player stat when a trinket is activated or deactivated.

        Arguments:
            time (float): Simulation time, in seconds, of activation.
            player (tbc_cat_sim.Player): Player object whose attributes will be
                modified.
            sim (tbc_cat_sim.Simulation): Simulation object controlling the
                fight execution.
            increment (float): Quantity to add to the player's existing stat
                value.
        """
        # Haste procs get handled separately from other raw stat buffs
        if self.stat_name == 'haste_rating':
            sim.apply_haste_buff(time, increment)
        else:
            old_value = getattr(player, self.stat_name)
            setattr(player, self.stat_name, old_value + increment)

            # Recalculate damage parameters when player stats change
            player.calc_damage_params(**sim.params)

    def activate(self, time, player, sim):
        """Activate the trinket buff upon player usage or passive proc.

        Arguments:
            time (float): Simulation time, in seconds, of activation.
            player (tbc_cat_sim.Player): Player object whose attributes will be
                modified by the trinket proc.
            sim (tbc_cat_sim.Simulation): Simulation object controlling the
                fight execution.
        """
        self.activation_time = time
        self.deactivation_time = time + self.proc_duration
        self.modify_stat(time, player, sim, self.stat_increment)
        sim.proc_end_times.append(self.deactivation_time)

        # Mark trinket as active
        self.active = True
        self.can_proc = False

        # Log if requested
        if sim.log:
            sim.combat_log.append(sim.gen_log(time, self.proc_name, 'applied'))

    def deactivate(self, player, sim):
        """Deactivate the trinket buff when the duration has expired.

        Arguments:
            player (tbc_cat_sim.Player): Player object whose attributes will be
                restored to their original values.
            sim (tbc_cat_sim.Simulation): Simulation object controlling the
                fight execution.
        """
        self.modify_stat(
            self.deactivation_time, player, sim, -self.stat_increment
        )
        self.active = False

        if sim.log:
            sim.combat_log.append(sim.gen_log(
                self.deactivation_time, self.proc_name, 'falls off'
            ))

    def update(self, time, player, sim):
        """Check for a trinket activation or deactivation at the specified
        simulation time, and perform associated bookkeeping.

        Arguments:
            time (float): Simulation time, in seconds.
            player (tbc_cat_sim.Player): Player object whose attributes will be
                modified by the trinket proc.
            sim (tbc_cat_sim.Simulation): Simulation object controlling the
                fight execution.
        """
        # First check if an existing buff has fallen off
        if self.active and (time > self.deactivation_time - 1e-9):
            self.deactivate(player, sim)

        # Then check whether the trinket is off CD and can now proc
        if (not self.can_proc
                and (time - self.activation_time > self.cooldown - 1e-9)):
            self.can_proc = True

        # Now decide whether a proc actually happens
        if self.apply_proc():
            self.activate(time, player, sim)

    def apply_proc(self):
        """Determine whether or not the trinket is activated at the current
        time. This method must be implemented by Trinket subclasses.

        Returns:
            proc_applied (bool): Whether or not the activation occurs.
        """
        return NotImplementedError(
            'Logic for trinket activation must be implemented by Trinket '
            'subclasses.'
        )


class ActivatedTrinket(Trinket):
    """Models an on-use trinket that is activated on cooldown as often as
    possible."""

    def apply_proc(self):
        """Determine whether or not the trinket is activated at the current
        time.

        Returns:
            proc_applied (bool): Whether or not the activation occurs.
        """
        # Activated trinkets follow the simple logic of being used as soon as
        # they are available.
        if self.can_proc:
            return True
        return False


class ProcTrinket(Trinket):
    """Models a passive trinket with a specified proc chance on hit or crit."""

    def __init__(
        self, stat_name, stat_increment, proc_name, chance_on_hit,
        chance_on_crit, proc_duration, cooldown
    ):
        """Initialize a generic trinket with key parameters.

        Arguments:
            stat_name (str): Name of the Player attribute that will be
                modified by the trinket activation. Must be a valid attribute
                of the Player class that can be modified. The one exception is
                haste_rating, which is separately handled by the Simulation
                object when updating timesteps for the sim.
            stat_increment (float): Amount by which the Player attribute is
                changed when the trinket is active.
            proc_name (str): Name of the buff that is applied when the trinket
                is active. Used for combat logging.
            chance_on_hit (float): Probability of a proc on a successful normal
                hit, between 0 and 1.
            chance_on_crit (float): Probability of a proc on a critical strike,
                between 0 and 1.
            proc_duration (int): Duration of the buff, in seconds.
            cooldown (int): Internal cooldown before the trinket can proc
                again.
        """
        Trinket.__init__(
            self, stat_name, stat_increment, proc_name, proc_duration,
            cooldown
        )
        self.chance_on_hit = chance_on_hit
        self.chance_on_crit = chance_on_crit
        self.proc_happened = False

    def check_for_proc(self, crit):
        """Perform random roll for a trinket proc upon a successful attack.

        Arguments:
            crit (bool): Whether the attack was a critical strike.
        """
        if not self.can_proc:
            self.proc_happened = False
        else:
            proc_roll = np.random.rand()
            proc_thresh = self.chance_on_crit if crit else self.chance_on_hit

            if proc_roll < proc_thresh:
                self.proc_happened = True
            else:
                self.proc_happened = False

    def apply_proc(self):
        """Determine whether or not the trinket is activated at the current
        time. For a proc trinket, it is assumed that a check has already been
        made for the proc when the most recent attack occurred.

        Returns:
            proc_applied (bool): Whether or not the activation occurs.
        """
        if self.can_proc and self.proc_happened:
            return True
        return False

    def reset(self):
        """Set trinket to fresh inactive state with no cooldown remaining."""
        Trinket.reset(self)
        self.proc_happened = False


# Library of recognized TBC trinkets and associated parameters

trinket_library = {
    'brooch': {
        'type': 'activated',
        'passive_stats': {
            'attack_power': 72,
        },
        'active_stats': {
            'stat_name': 'attack_power',
            'stat_increment': 278,
            'proc_name': 'Lust for Battle',
            'proc_duration': 20,
            'cooldown': 120,
        },
    },
}
