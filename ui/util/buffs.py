
def apply_buffs(
        unbuffed_ap, unbuffed_strength, unbuffed_agi, unbuffed_hit,
        unbuffed_crit, unbuffed_mana, unbuffed_int, unbuffed_spirit,
        unbuffed_mp5, weapon_damage, raid_buffs, consumables, bshout_options
):
    """Takes in unbuffed player stats, and turns them into buffed stats based
    on specified consumables and raid buffs. This function should only be
    called if the "Buffs" option is not checked in the exported file from
    Seventy Upgrades, or else the buffs will be double counted!"""

    # Determine "raw" AP, crit, and mana not from Str/Agi/Int
    raw_ap_unbuffed = unbuffed_ap / 1.1 - 2 * unbuffed_strength - unbuffed_agi
    raw_crit_unbuffed = unbuffed_crit - unbuffed_agi / 25
    raw_mana_unbuffed = unbuffed_mana - 15 * unbuffed_int

    # Augment all base stats based on specified buffs
    stat_multiplier = 1 + 0.1 * ('kings' in raid_buffs)
    added_stats = 18 * ('motw' in raid_buffs)

    buffed_strength = stat_multiplier * (unbuffed_strength + 1.03 * (
            added_stats + 98 * ('str_totem' in raid_buffs)
            + 20 * ('scroll_str' in consumables)
    ))
    buffed_agi = stat_multiplier * (unbuffed_agi + 1.03 * (
            added_stats + 88 * ('agi_totem' in raid_buffs)
            + 35 * ('agi_elixir' in consumables) + 20 * ('food' in consumables)
            + 20 * ('scroll_agi' in consumables)
    ))
    buffed_int = stat_multiplier * (unbuffed_int + 1.2 * 1.03 * (
            added_stats + 40 * ('ai' in raid_buffs)
            + 30 * ('draenic' in consumables)
    ))
    buffed_spirit = stat_multiplier * (unbuffed_spirit + 1.03 * (
            added_stats + 50 * ('spirit' in raid_buffs)
            + 20 * ('food' in consumables) + 30 * ('draenic' in consumables)
    ))

    # Now augment secondary stats
    ap_mod = 1.1 * (1 + 0.1 * ('unleashed_rage' in raid_buffs))
    bshout_ap = (
            ('bshout' in raid_buffs) * (305 + 70 * ('trinket' in bshout_options))
            * (1. + 0.25 * ('talent' in bshout_options))
    )
    buffed_attack_power = ap_mod * (
            raw_ap_unbuffed + 2 * buffed_strength + buffed_agi
            + 264 * ('might' in raid_buffs) + bshout_ap
            + 125 * ('trueshot_aura' in raid_buffs)
    )
    added_crit_rating = (
            20 * ('agi_elixir' in consumables)
            + 14 * ('weightstone' in consumables)
    )
    buffed_crit = (
            raw_crit_unbuffed + buffed_agi / 25 + added_crit_rating / 22.1
    )
    buffed_hit = (
            unbuffed_hit + 1 * ('heroic_presence' in raid_buffs)
    )
    buffed_mana_pool = raw_mana_unbuffed + buffed_int * 15
    buffed_mp5 = unbuffed_mp5 + 49 * ('wisdom' in raid_buffs)
    buffed_weapon_damage = (
            12 * ('weightstone' in consumables) + weapon_damage
    )

    return {
        'strength': buffed_strength,
        'agility': buffed_agi,
        'intellect': buffed_int,
        'spirit': buffed_spirit,
        'attackPower': buffed_attack_power,
        'crit': buffed_crit,
        'hit': buffed_hit,
        'weaponDamage': buffed_weapon_damage,
        'mana': buffed_mana_pool,
        'mp5': buffed_mp5
    }

