import random
import math
from asteval import Interpreter
import asyncio
import json

lock = asyncio.Lock()

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

status_handler = {}
item_handler = {}

def register_status(status_name):
    def decorator(func):
        status_handler[status_name] = func
        return func
    return decorator

def register_item(item_name):
    def decorator(func):
        item_handler[item_name] = func
        return func
    return decorator

def calc_hp(mon: dict, skelemon: dict) -> int:
    return math.floor(skelemon['basehp'] + 3 * mon['lvl'] + 0.3 * mon['lvl']**2 + 4 * mon['stats']['vit'])

def calc_next_level_exp(mon: dict) -> int:
    statsum = sum(mon['stats'].values())
    sauce = (statsum + mon['maxhp']) / 109
    return math.floor(1 + 8 * mon['lvl']**2 + 8 * sauce)

def drop_exp(winner: dict, loser: dict) -> int:
    lsauce = (sum(loser['stats'].values()) + loser['maxhp']) / 109
    saucediff = max(lsauce - (sum(winner['stats'].values()) + winner['maxhp']) / 109, 1)
    lvldiff = max(loser['lvl'] - winner['lvl'], 1)
    return math.floor(1 + lvldiff * loser['lvl']**2 + saucediff * lsauce)

def drop_sunlight(loser: dict) -> int:
    base_sunlight = 5
    statsum = sum(loser['stats'].values())
    sauce = (statsum + loser['maxhp']) / 109
    return base_sunlight * sauce

def process_lvls(mon: dict, skelemon: dict, exp: int) -> None:
    while True:
        intdiv = math.floor(exp / mon['nextlvl'])
        if intdiv > 0:
            exp -= mon['nextlvl']
            mon['lvl'] += 1
            mon['maxhp'] = calc_hp(mon, skelemon)
            mon['currhp'] = mon['maxhp']
            lvl_up_stats(mon, skelemon)
            mon['nextlvl'] = calc_next_level_exp(mon)
        else:
            mon['nextlvl'] -= exp
            break

def saturation(stat: int) -> float:
    return sum((100 * n)/(100 + n**2) for n in range(1, stat + 1))

def AR(scales: dict, base: float, stats: dict) -> float:
    return sum(scaling[scale] * base * (saturation(stats[stat]) / 230) for stat, scale in scales.items())

def damage(attacker: dict, defender: dict, skill: dict) -> float:
    if attacker['type'] not in type_adv[defender['type']]:
        typemult = 1
    else:
        typemult = type_adv[defender['type']][attacker['type']]
    return AR(skill['scaling'], skill['basedmg'], attacker['stats']) * (100 / (100 + defender['stats']['def'])) * typemult

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
    base_hit = 0.50
    max_hit = 0.98
    min_hit = 0.50
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
    return base_poison * attacker['stats']['arc'] * 0.5 * (100 / (100 + defender['stats']['res']))

def flee_chance(fleer: dict, fleeing_from: dict) -> float:
    base_chance = 0.5
    max_chance = 0.95
    min_chance = 0.30
    flee_chance = base_chance + ((fleer['stats']['adp'] - fleeing_from['stats']['adp']) * 0.01)
    return max(min(flee_chance, max_chance), min_chance)

#status functions-------------------------------------------------------------------------

@register_status(status_name="Paralysis")
def handle_paralysis(attacker: dict, defender: dict) -> str:
    if random.random() > status_unproc_chance(attacker, defender):
        attacker['statuses'].remove("Paralysis")
        return f"attacker is no longer paralyzed\n"
    else:
        return f"attacker is paralyzed"
    
@register_status(status_name="Poison")
def handle_poison(attacker: dict, defender: dict) -> str:
    if random.random() > status_unproc_chance(attacker, defender):
        attacker['statuses'].remove("Poison")
        return f"attacker is no longer poisoned\n"
    else:
        damage = poison_damage(attacker, defender)
        attacker['currhp'] -= damage
        return f"attacker took {damage} poison damage\n"
    
@register_status(status_name="BBP")
def handle_bbp_status(attacker: dict, **kwargs) -> str:
    attacker['stats']['str'] = attacker['stats']['str'] * 10000
    attacker['stats']['def'] = attacker['stats']['def'] / 10000
    attacker['statuses'].remove("BBP")
    attacker['statuses'].append("antiBBP")
    return "Attacker is under the effect of Beast Blood Pellet\n"

@register_status(status_name="antiBBP")
def handle_antibbp_status(attacker: dict, **kwargs) -> str:
    attacker['stats']['str'] = math.floor(attacker['stats']['str'] / 10000)
    attacker['stats']['def'] = math.floor(attacker['stats']['def'] * 10000)
    attacker['statuses'].remove("antiBBP")
    return "Attacker is no longer under the effect of Beast Blood Pellet"

#item functions------------------------------------------------------------------------------

def heal(percent: float, mon: dict) -> str:
    if mon['gaol']:
        return f"Cannont heal Gricklemon in Gaol"
    heals = math.floor(mon['maxhp'] * percent)
    currenthp = mon['currhp']
    mon['currhp'] = min(mon['currhp'] + heals, mon['maxhp'])
    return f"healed for {mon['currhp'] - currenthp} hp"

@register_item(item_name="Estus")
def handle_estus(mon: dict, **kwargs) -> str:
    message = heal(percent=0.30, mon=mon)
    return message

@register_item(item_name="Blood Vial")
def handle_blood_vial(mon: dict, **kwargs) -> str:
    message = heal(percent=0.50, mon=mon)
    return message

@register_item(item_name="Stonesword Key")
def handle_stone_sword_key(monname: str, mon: dict, userid: str, **kwargs) -> str:
    if mon['gaol']:
        mon['gaol'] = False
        mon['currhp'] = mon['maxhp']
        with lock and open('gaol.json') as f:
            gaols = json.load(f)
        gaols[userid].remove(monname)
        with lock and open('gaol.json', 'w') as f:
            json.dump(gaols, f, indent=2)
        return "Mon released from Gaol"
    else: return "Mon not in Gaol\0"

@register_item(item_name="Beast Blood Pellet")
def handle_bbp_item(mon: dict, **kwargs) -> str:
    mon['statuses'].append("BBP")
    return "Applied Beast Blood Pellet affect"