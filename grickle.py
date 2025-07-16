import random
import math
from asteval import Interpreter

aeval = Interpreter()

type_adv = { #defending then attacker
    "Fire": {
        "Water": 1.3,
        "Grass": 0.7
    },
    "Water": {
        "Fire": 0.7,
        "Grass": 1.3 
    },
    "Grass": {
        "Fire": 0.7,
        "Water": 1.3
    }
}

scaling = {"-": 0, "E": 0.25, "D": 0.6, "C": 0.9, "B": 1.4, "A": 1.75, "S": 2.2}

def calc_hp(mon: dict, skelemon: dict) -> int:
    return math.floor(skelemon['basehp'] + 3 * mon['lvl'] + 0.3 * mon['lvl']**2 + 4 * mon['stats']['vit'])

def calc_next_level_exp(mon: dict) -> int:
    statsum = sum(mon['stats'].values())
    sauce = (statsum + mon['maxhp']) / 109
    return math.floor(1 + 4 * mon['lvl'] + 4 * sauce**2)

def drop_exp(winner: dict, loser: dict) -> int:
    lsauce = (sum(loser['stats'].values()) + loser['maxhp']) / 109
    saucediff = max(lsauce - (sum(winner['stats'].values()) + winner['maxhp']) / 109, 1)
    lvldiff = max(loser['lvl'] - winner['lvl'], 1)
    return math.floor(1 + lvldiff * loser['lvl'] + saucediff * lsauce**2)

def saturation(stat: int) -> float:
    return sum((100 * n)/(100 + n**2) for n in range(1, stat + 1))

def AR(scales: dict, base: float, stats: dict) -> float:
    return sum(scaling[scale] * base * (saturation(stats[stat]) / 230) for stat, scale in scales.items())

def damage(attacker: dict, defender: dict, skill: dict) -> float:
    if attacker['type'] not in type_adv[defender['type']]:
        typemult = 1
    else:
        typemult = type_adv[defender['type']][attacker['type']]
    return AR(skill['scaling'], skill['base'], attacker['stats']) * (100 / (100 + defender['stats']['def'])) * typemult

def make_growth_function(expr: str):
    def growth(lvl: int):
        aeval.symtable['lvl'] = lvl
        aeval.symtable['floor'] = math.floor
        aeval.symtable['log'] = math.log
        return aeval(expr)
    return growth

def lvl_up_stats(mon: dict, monskeleton: dict) -> None:
    growth_funcs = {stat: make_growth_function(expr) for stat, expr in monskeleton['statscales'].items()}
    mon['stats'] = {stat: func(mon['lvl']) for stat, func in growth_funcs.items()}

def hit_chance(attacker: dict, defender: dict) -> float:
    base_hit = 0.80
    max_hit = 0.98
    min_hit = 0.10
    hit_chance = base_hit + ((attacker['stats']['adp'] - defender['stats']['adp']) * 0.01)
    return max(min(hit_chance, max_hit), min_hit)

def status_proc_chance(attacker: dict, defender: dict) -> float:
    base_chance = 0.3
    max_chance = 0.95
    min_chance = 0.10
    hit_chance = base_chance + ((attacker['stats']['arc'] - defender['stats']['res']) * 0.02)
    return max(min(hit_chance, max_chance), min_chance)

def status_unproc_chance(attacker: dict, defender: dict) -> float:
    base_chance = 0.10
    max_chance = 0.50
    min_chance = 0.05
    unhit_chance = base_chance + ((defender['stats']['res'] - attacker['stats']['arc']) * 0.02)
    return max(min(unhit_chance, max_chance), min_chance)

def poison_damage(attacker: dict, defender: dict) -> float:
    base_poison = 2
    return base_poison * attacker['arc'] * 0.5 * (100 / (100 + defender['res']))
