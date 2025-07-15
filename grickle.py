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

scaling = {"E": 0, "D": 0.25, "C": 0.6, "B": 0.9, "A": 1.4, "S": 1.75}

def calc_hp(lvl: int, vit: int, base_hp: int) -> int:
    return math.floor(base_hp + 3 * lvl + 0.3 * lvl**2 + 4 * vit)

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

def lvl_up_stats(mon: dict) -> None:
    growth_funcs = {stat: make_growth_function(expr) for stat, expr in mon['statscales'].items()}
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
