import customtkinter as ctk
import numpy as np
import json
import asyncio
import re

import grickle

lock = asyncio.Lock()

with lock and open('gricklemon.json') as f:
    mons = json.load(f)
with lock and open('skills.json') as f:
    skills = json.load(f)
with lock and open('items.json') as f:
    items = json.load(f)
with lock and open('boss-mons.json') as f:
    bosses = json.load(f)
with lock and open('banners.json') as f:
    banners = json.load(f)
with lock and open('stocks.json') as f:
    stocks = json.load(f)
with lock and open('typing.json') as f:
    typings = json.load(f)

monlist = list(mons.keys())
monlist.append('new')
skilllist = list(skills.keys())
skilllist.append("new")
itemlist = list(items.keys())
itemlist.append("new")
bosslist = list(bosses.keys())
bosslist.append('new')
bannerlist = list(banners.keys())
bannerlist.append('new')
bannerlist.remove("active")
bannerlist.remove('change-date')
stocklist = list(stocks.keys())
stocklist.append("new")
typelist = list(typings.keys())
typelist.append('new')

stat_list = ['vit', 'str', 'dex', 'int', 'fth', 'adp', 'arc', 'res', 'def']
usebanner_list = list(banners.keys())
usebanner_list.remove('active')
usebanner_list.remove('change-date')

def is_non_neg_dec(value):
    return re.fullmatch(r"^\d*\.?\d*$", value) is not None or value == ""

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()

    valid_num = root.register(is_non_neg_dec)

    root.title("Mon Editor")
    root.geometry("1920x1080")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    tabview = ctk.CTkTabview(master=root)
    tabview.grid(row=0, column=0, sticky='nsew')

    gtab = tabview.add("Gricklemon Editor")
    stab = tabview.add("Skill Editor")
    itab = tabview.add("Item Editor")
    btab = tabview.add("Boss Editor")
    bantab = tabview.add("Banner Editor")
    stotab = tabview.add("Stock Editor")
    ttab = tabview.add("Typing Editor")

    gtab.columnconfigure(0, weight=1)
    gtab.rowconfigure(0, weight=1)
    gtab_scroll = ctk.CTkScrollableFrame(master=gtab)
    gtab_scroll.grid(row=0, column=0, sticky='nsew')

    btab.columnconfigure(0, weight=1)
    btab.rowconfigure(0, weight=1)
    btab_scroll = ctk.CTkScrollableFrame(master=btab)
    btab_scroll.grid(row=0, column=0, sticky='nsew')

    #gricklemon editor-------------------------------------------------------------------------

    monrarity_list = ['Rare', 'Legendary', 'Incandescent']
    monlvlscale_list = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    monlvlscale_label_dict = {}
    monskills_labels_dict = {}
    monskills_del_dict = {}
    monstats_labels_dict = {}
    monstats_entries_dict = {}

    def mon_select_callback(mon):
        global monskills_list
        global monstat_growth_funcs
        if mon == "new":
            monname_entry.configure(textvariable=ctk.StringVar(master=gtab_scroll, value=""))
            selected_monbanner.set("Normal")
            selected_monrarity.set("Rare")
            selected_montype.set("Fire")
            monhp_entry.configure(textvariable=ctk.StringVar(master=gtab_scroll, value=""))
            mondescription_text.delete('0.0', 'end')
            monskills_list.clear()
            render_monskills()
            monstat_growth_funcs.clear()
            for stat in stat_list:
                for lvl in monlvlscale_list:
                    monstats_entries_dict[stat][lvl].configure(textvariable=ctk.StringVar(master=gtab_scroll, value=""))
            mon_save_create.configure(text="Create Gricklemon")
            mon_save_create.configure(command=mon_create_callback)
        else:
            monname_entry.configure(textvariable=ctk.StringVar(master=gtab_scroll, value=mon))
            selected_monbanner.set(mons[mon]['banner'])
            selected_monrarity.set(mons[mon]['rarity'])
            selected_montype.set(mons[mon]['type'])
            monhp_entry.configure(textvariable=ctk.StringVar(master=gtab_scroll, value=mons[mon]['basehp']))
            mondescription_text.delete('0.0', 'end')
            mondescription_text.insert('0.0', mons[mon]['description'])
            monskills_list.clear()
            monskills_list.extend([skill for skill in mons[mon]['skills']])
            render_monskills()
            monstat_growth_funcs.clear()
            monstat_growth_funcs.update({stat: grickle.make_growth_function(expr) for stat, expr in mons[mon]['statscales'].items()})
            for stat in stat_list:
                for lvl in monlvlscale_list:
                    monstats_entries_dict[stat][lvl].configure(textvariable=ctk.StringVar(master=gtab_scroll, value=monstat_growth_funcs[stat](lvl)))
            mon_save_create.configure(text="Save Changes")
            mon_save_create.configure(command=mon_save_callback)

    def monskill_select_callback(skill):
        if skill in monskills_list or len(monskills_list) == 4:
            return
        monskills_list.append(skill)
        render_monskills()

    def monskill_del_callback(skill):
        if len(monskills_list) == 1:
            return
        monskills_list.remove(skill)
        render_monskills()

    def mon_save_callback():
        mon = mon_select.get()
        new_monname = monname_entry.get()
        if mon != new_monname and new_monname in mons:
            return
        new_monhp = int(monhp_entry.get())
        new_description = mondescription_text.get('0.0', 'end')
        if "" in (new_monname, new_monhp, new_description):
            return
        coeff_dict = {}
        for stat in stat_list:
            coeff_dict[stat] = np.polyfit(np.array(monlvlscale_list), np.array(sorted([int(statlvl.get()) for lvl, statlvl in monstats_entries_dict[stat].items()])), 2).tolist()
        mons[new_monname] = {'banner': monbanner_select.get(), 'rarity': monrarity_select.get(), 'type': montype_select.get(), 'basehp': new_monhp, 'description': new_description, 'statscales': {stat: f"floor({round(coeff_dict[stat][0], 5)} * lvl**2 + {round(coeff_dict[stat][1], 5)} * lvl + {round(coeff_dict[stat][2], 2)})" for stat in stat_list}, 'skills': {skill: skills[skill] for skill in monskills_list}}
        for skill in mons[new_monname]['skills']:
            mons[new_monname]['skills'][skill]['equiped'] = True
        if new_monname != mon:
            del mons[mon]
            monlist.remove(mon)
            monlist.insert(0, new_monname)
            mon_select.configure(values=monlist)
            selected_mon.set(new_monname)
        with lock and open('gricklemon.json', 'w') as f:
            json.dump(mons, f, indent=2)

    def mon_create_callback():
        monname = monname_entry.get()
        monhp = int(monhp_entry.get())
        description = mondescription_text.get('0.0', 'end')
        if "" in (monname, monhp, description) or monname in mons:
            return
        coeff_dict = {}
        for stat in stat_list:
            coeff_dict[stat] = np.polyfit(np.array(monlvlscale_list), np.array(sorted([int(statlvl.get()) for lvl, statlvl in monstats_entries_dict[stat].items()])), 2).tolist()
        mons[monname] = {'banner': monbanner_select.get(), 'rarity': monrarity_select.get(), 'type': montype_select.get(), 'basehp': monhp, 'description': description, 'statscales': {stat: f"floor({round(coeff_dict[stat][0], 5)} * lvl**2 + {round(coeff_dict[stat][1], 5)} * lvl + {round(coeff_dict[stat][2], 2)})" for stat in stat_list}, 'skills': {skill: skills[skill] for skill in monskills_list}}
        for skill in mons[monname]['skills']:
            mons[monname]['skills'][skill]['equiped'] = True
        with lock and open('gricklemon.json', 'w') as f:
            json.dump(mons, f, indent=2)
        monlist.insert(0, monname)
        mon_select.configure(values=monlist)
        selected_mon.set(monname)
        mon_select_callback(monname)

    selected_mon = ctk.StringVar(master=gtab_scroll, value=monlist[0])
    mon_select = ctk.CTkOptionMenu(master=gtab_scroll, values=monlist, variable=selected_mon, command=mon_select_callback)
    mon_select.grid(row=0, column=0, sticky='w')

    mon_save_create = ctk.CTkButton(master=gtab_scroll, text="Save Changes", command=mon_save_callback)
    mon_save_create.grid(row=0, column=2, sticky='w')

    monname_label = ctk.CTkLabel(master=gtab_scroll, text="Name:")
    monname_label.grid(row=1, column=0, sticky='w', pady=(10,0))

    monname_entry = ctk.CTkEntry(master=gtab_scroll, textvariable=ctk.StringVar(master=gtab_scroll, value=mon_select.get()))
    monname_entry.grid(row=2, column=0, sticky='w')

    monbanner_label = ctk.CTkLabel(master=gtab_scroll, text="Banner:")
    monbanner_label.grid(row=3, column=0, sticky='w', pady=(10,0))

    selected_monbanner = ctk.StringVar(master=gtab_scroll, value=mons[mon_select.get()]['banner'])
    monbanner_select = ctk.CTkOptionMenu(master=gtab_scroll, values=usebanner_list, variable=selected_monbanner)
    monbanner_select.grid(row=4, column=0, sticky='w')

    monrarity_label = ctk.CTkLabel(master=gtab_scroll, text='Rarity:')
    monrarity_label.grid(row=5, column=0, sticky='w', pady=(10,0))

    selected_monrarity = ctk.StringVar(master=gtab_scroll, value=mons[mon_select.get()]['rarity'])
    monrarity_select = ctk.CTkOptionMenu(master=gtab_scroll, values=monrarity_list, variable=selected_monrarity)
    monrarity_select.grid(row=6, column=0, sticky='w')

    montype_label = ctk.CTkLabel(master=gtab_scroll, text='Type:')
    montype_label.grid(row=7, column=0, sticky='w', pady=(10,0))

    selected_montype = ctk.StringVar(master=gtab_scroll, value=mons[mon_select.get()]['type'])
    montype_select = ctk.CTkOptionMenu(master=gtab_scroll, values=list(typings.keys()), variable=selected_montype)
    montype_select.grid(row=8, column=0, sticky='w')

    monhp_label = ctk.CTkLabel(master=gtab_scroll, text='Base Hp:')
    monhp_label.grid(row=9, column=0, sticky='w', pady=(10,0))

    monhp_entry = ctk.CTkEntry(master=gtab_scroll, validate="key", validatecommand=(valid_num, "%P"), textvariable=ctk.StringVar(master=gtab_scroll, value=mons[mon_select.get()]['basehp']))
    monhp_entry.grid(row=10, column=0, sticky='w')

    mondescription_label = ctk.CTkLabel(master=gtab_scroll, text='Description:')
    mondescription_label.grid(row=11, column=0, sticky='w', pady=(10,0))

    mondescription = mons[mon_select.get()]['description']
    mondescription_text = ctk.CTkTextbox(master=gtab_scroll)
    mondescription_text.insert('0.0', mondescription)
    mondescription_text.grid(row=12, column=0, columnspan=2, sticky='nsew')

    monskills_label = ctk.CTkLabel(master=gtab_scroll, text="Skills:")
    monskills_label.grid(row=13, column=0, sticky='w', pady=(10,0))

    selected_monskill = ctk.StringVar(master=gtab_scroll, value=list(skills.keys())[0])
    monskill_select = ctk.CTkOptionMenu(master=gtab_scroll, values=list(skills.keys()), variable=selected_monskill, command=monskill_select_callback)
    monskill_select.grid(row=13, column=1, sticky='w')

    monskills_scroll = ctk.CTkScrollableFrame(master=gtab_scroll)
    monskills_scroll.grid(row=14, column=0, columnspan=2, sticky='nsew')
    monskills_scroll.grid_columnconfigure((0,1), weight=1)

    global monskills_list
    monskills_list = [skill for skill in mons[mon_select.get()]['skills']]

    def render_monskills():
        for skill in monskills_labels_dict:
            monskills_labels_dict[skill].destroy()
        monskills_labels_dict.clear()
        for skill in monskills_del_dict:
            monskills_del_dict[skill].destroy()
        monskills_del_dict.clear()
        row = 0
        for skill in monskills_list:
            monskills_labels_dict[skill] = ctk.CTkLabel(master=monskills_scroll, text=f'{skill}:')
            monskills_labels_dict[skill].grid(row=row, column=0, sticky='w', pady=(10,0))

            monskills_del_dict[skill] = ctk.CTkButton(master=monskills_scroll, text='Delete', fg_color='red', command=lambda s=skill: monskill_del_callback(s))
            monskills_del_dict[skill].grid(row=row, column=1, sticky='w', pady=(10,0))

            row += 1
    render_monskills()

    monstatscale_label = ctk.CTkLabel(master=gtab_scroll, text='Stat Scales:')
    monstatscale_label.grid(row=15, column=0, sticky='w', pady=(10,0))

    col = 1
    for lvl in monlvlscale_list:
        monlvlscale_label_dict[lvl] = ctk.CTkLabel(master=gtab_scroll, text=f'lvl: {lvl}')
        monlvlscale_label_dict[lvl].grid(row=15, column=col, sticky='w', pady=(10,0))

        col += 1

    global monstat_growth_funcs
    monstat_growth_funcs = {stat: grickle.make_growth_function(expr) for stat, expr in mons[mon_select.get()]['statscales'].items()}

    row = 16
    for stat in stat_list:
        col = 0 
        monstats_labels_dict[stat] = ctk.CTkLabel(master=gtab_scroll, text=f'{stat}: ')
        monstats_labels_dict[stat].grid(row=row, column=col, sticky='w', pady=(10,0))

        col+=1

        monstats_entries_dict[stat] = {}
        for lvl in monlvlscale_list:
            monstats_entries_dict[stat][lvl] = ctk.CTkEntry(master=gtab_scroll, validate="key", validatecommand=(valid_num, "%P"), textvariable=ctk.StringVar(master=gtab_scroll, value=str(monstat_growth_funcs[stat](lvl))))
            monstats_entries_dict[stat][lvl].grid(row=row, column=col, sticky='w', pady=(10,0))

            col += 1

        row += 1

    #skill editor---------------------------------------------------------------------------------------

    skillscaling_list = ["S", "A", "B", "C", "D", "E", "-"]
    skillstat_list = ['str', 'dex', 'int', 'fth', 'arc']
    skill_rarity = ['Common', 'Uncommon', 'Rare', 'Legendary', 'Incandescent']
    status_effects = ['Poison', 'Paralysis']
    skillstat_label_dict = {}
    skillstat_option_dict = {}
    skillstat_selected_dict = {}
    skillstatus_label_dict = {}
    skillstatus_dict = {}
    skillstatus_check_dict = {}

    def skill_select_callback(skill):
        if skill == "new":
            skillname_entry.configure(textvariable=ctk.StringVar(master=stab, value=""))
            selected_skillbanner.set("Normal")
            selected_skillrarity.set("Common")
            skillbasedmg_entry.configure(textvariable=ctk.StringVar(master=stab, value=""))
            for stat in skillstat_list:
                skillstat_selected_dict[stat].set("-")
            for status in status_effects:
                skillstatus_check_dict[status].deselect()
            skilldescription_textbox.delete("0.0", "end")
            skill_save_create.configure(text="Create Skill")
            skill_save_create.configure(command=skill_create_callback)
        else:
            skillname_entry.configure(textvariable=ctk.StringVar(master=stab, value=skill))
            selected_skillbanner.set(skills[skill]['banner'])
            selected_skillrarity.set(skills[skill]['rarity'])
            skillbasedmg_entry.configure(textvariable=ctk.StringVar(master=stab, value=str(skills[skill]['basedmg'])))
            for stat in skillstat_list:
                skillstat_selected_dict[stat].set(skills[skill]['scaling'][stat])
            for status in status_effects:
                if status in skills[skill]['statuses']:
                    skillstatus_check_dict[status].select()
            skilldescription_textbox.delete("0.0", 'end')
            skilldescription_textbox.insert('0.0', skills[skill]['description'])
            skill_save_create.configure(text="Save Changes")
            skill_save_create.configure(command=skill_save_callback)

    def skill_save_callback():
        skill = skill_select.get()
        new_skillname = skillname_entry.get()
        if new_skillname != skill and new_skillname in skills:
            return
        new_skillbasedmg = int(skillbasedmg_entry.get())
        new_skilldescription = skilldescription_textbox.get('0.0', 'end')
        if "" in (new_skillname, new_skillbasedmg, new_skilldescription):
            return
        skills[new_skillname] = {'banner': skillbanner_select.get(), 'rarity': skillrarity_select.get(), 'basedmg': new_skillbasedmg, 'description': new_skilldescription, 'scaling': {stat: scale.get() for stat, scale in skillstat_option_dict.items()}, 'statuses': [status for status in status_effects if skillstatus_check_dict[status].get() == "True"]}
        if skill != new_skillname:
            del skills[skill]
            skilllist.remove(skill)
            skilllist.insert(0, new_skillname)
            skill_select.configure(values=skilllist)
            selected_skill.set(new_skillname)
        with lock and open('skills.json', 'w') as f:
            json.dump(skills, f, indent=2)

    def skill_create_callback():
        skillname = skillname_entry.get()
        skillbasedmg = int(skillbasedmg_entry.get())
        description = skilldescription_textbox.get('0.0', 'end')
        if "" in (skillname, skillbasedmg, description) or skillname in skills:
            return
        skills[skillname] = {'banner': skillbanner_select.get(), 'rarity': skillrarity_select.get(), 'basedmg': skillbasedmg, 'description': description, 'scaling': {stat: scale.get() for stat, scale in skillstat_option_dict.items()}, 'statuses': [status for status in status_effects if skillstatus_check_dict[status].get() == "True"]}
        with lock and open('skills.json', 'w') as f:
            json.dump(skills, f, indent=2)
        skilllist.insert(0, skillname)
        skill_select.configure(values=skilllist)
        selected_skill.set(skillname)
        skill_select_callback(skillname)

    selected_skill = ctk.StringVar(master=stab, value=skilllist[0])
    skill_select = ctk.CTkOptionMenu(master=stab, values=skilllist, command=skill_select_callback, variable=selected_skill)
    skill_select.grid(row=0, column=0, sticky='w')

    skillname_label = ctk.CTkLabel(master=stab, text="Name:")
    skillname_label.grid(row=1, column=0, sticky='w', pady=(10,0))

    skillname_entry = ctk.CTkEntry(master=stab, textvariable=ctk.StringVar(master=stab, value=skill_select.get()))
    skillname_entry.grid(row=2, column=0, sticky='w', pady=(10,0))

    skillbanner_label = ctk.CTkLabel(master=stab, text="Banner:")
    skillbanner_label.grid(row=3, column=0, sticky='w', pady=(10,0))

    selected_skillbanner = ctk.StringVar(master=stab, value=skills[skill_select.get()]['banner'])
    skillbanner_select = ctk.CTkOptionMenu(master=stab, values=usebanner_list, variable=selected_skillbanner)
    skillbanner_select.grid(row=4, column=0, sticky='w')

    skillrarity_label = ctk.CTkLabel(master=stab, text="Rarity:")
    skillrarity_label.grid(row=5, column=0, sticky='w', pady=(10,0))

    selected_skillrarity = ctk.StringVar(master=stab, value=skills[skill_select.get()]['rarity'])
    skillrarity_select = ctk.CTkOptionMenu(master=stab, values=skill_rarity, variable=selected_skillrarity)
    skillrarity_select.grid(row=6, column=0, sticky='w')

    skillbasedmg_label = ctk.CTkLabel(master=stab, text="Base Damage")
    skillbasedmg_label.grid(row=7, column=0, sticky='w', pady=(10,0))

    skillbasedmg_entry = ctk.CTkEntry(master=stab, validate="key", validatecommand=(valid_num, "%P"), textvariable=ctk.StringVar(master=stab, value=skills[skill_select.get()]['basedmg']))
    skillbasedmg_entry.grid(row=8, column=0, sticky='w')

    statrow = 9
    for stat in skillstat_list:
        skillstat_label_dict[stat] = ctk.CTkLabel(master=stab, text=f"{stat}:")
        skillstat_label_dict[stat].grid(row=statrow, column=0, sticky='w', pady=(10,0))

        skillstat_selected_dict[stat] = ctk.StringVar(master=stab, value=skills[skill_select.get()]['scaling'][stat])

        skillstat_option_dict[stat] = ctk.CTkOptionMenu(master=stab, values=skillscaling_list, variable=skillstat_selected_dict[stat], width=20)
        skillstat_option_dict[stat].grid(row=statrow, column=1, sticky='w', pady=(10,0))

        statrow += 1

    for status in status_effects:
        skillstatus_label_dict[status] = ctk.CTkLabel(master=stab, text=f"{status}:")
        skillstatus_label_dict[status].grid(row=statrow, column=0, sticky='w', pady=(10,0))

        if stat in skills[skill_select.get()]['statuses']:
            statbool = "True"
        else:
            statbool = "False"
        skillstatus_dict[status] = ctk.StringVar(master=stab, value=statbool)

        skillstatus_check_dict[status] = ctk.CTkCheckBox(master=stab, text="", variable=skillstatus_dict[status], onvalue="True", offvalue="False")
        skillstatus_check_dict[status].grid(row=statrow, column=1, sticky='w', pady=(10,0))

        statrow += 1

    skilldescription_label = ctk.CTkLabel(master=stab, text="Description:")
    skilldescription_label.grid(row=statrow, column=0, sticky='w', pady=(10,0))

    statrow += 1
    skilldescription = skills[skill_select.get()]['description']
    skilldescription_textbox = ctk.CTkTextbox(master=stab)
    skilldescription_textbox.insert("0.0", skilldescription)
    skilldescription_textbox.grid(row=statrow, column=0, columnspan=2, sticky='ew')

    statrow += 1
    skill_save_create = ctk.CTkButton(master=stab, text="Save Changes", command=skill_save_callback)
    skill_save_create.grid(row=statrow, column=0, sticky='w', pady=(10,0))

    #item editor------------------------------------------------------------------------------------------

    itemrarity_list = ['Common', 'Uncommon', 'Rare', 'Legendary', "Incandescent", 'Key-Item']

    def item_select_callback(item):
        if item == "new":
            itemname_entry.configure(textvariable=ctk.StringVar(master=itab, value=""))
            selected_itemrarity.set("Common")
            itemprice_entry.configure(textvariable=ctk.StringVar(master=itab, value=""))
            itemconsumable_switch.deselect()
            itemstatuseffect_switch.deselect()
            itemnobattleonly_switch.deselect()
            itemdescription_textbox.delete("0.0", "end")
            item_save_or_create.configure(text="Create Item")
            item_save_or_create.configure(command=item_create_callback)
        else:
            itemname_entry.configure(textvariable=ctk.StringVar(master=itab, value=item))
            selected_itemrarity.set(items[item]['rarity'])
            itemprice_entry.configure(textvariable=ctk.StringVar(master=itab, value=str(items[item]['price'])))
            itemconsumable.set(str(items[item]['consumable']))
            itemstatuseffect.set(str(items[item]['statuseffect']))
            itemnobattleonly.set(str(items[item]['nobattleonly']))
            itemdescription_textbox.delete("0.0", "end")
            itemdescription_textbox.insert("0.0", items[item]['description'])
            item_save_or_create.configure(text="Save Changes")
            item_save_or_create.configure(command=item_save_callback)

    def itemconsumable_switch_callback():
        if itemconsumable_switch.get() == "False":
            itemnobattleonly_switch.deselect()
            itemstatuseffect_switch.deselect()

    def itemstatuseffect_switch_callback():
        if itemstatuseffect_switch.get() == "True":
            itemconsumable_switch.select()
            itemnobattleonly_switch.deselect()

    def itemnobattleonly_switch_callback():
        if itemnobattleonly_switch.get() == "True":
            itemconsumable_switch.select()
            itemstatuseffect_switch.deselect()

    def item_save_callback():
        item = item_select.get()
        new_name = itemname_entry.get()
        if new_name != item and new_name in items:
            return
        new_price = float(itemprice_entry.get())
        new_rarity = itemrarity_select.get()
        new_description = itemdescription_textbox.get("0.0", "end")
        if "" in (new_name, new_price, new_description):
            return
        consumable = bool(itemconsumable_switch.get())
        if itemconsumable_switch.get() == "False":
            consumable = False
        statuseffect = bool(itemstatuseffect_switch.get())
        if itemstatuseffect_switch.get() == "False":
            statuseffect = False
        nobattleonly = bool(itemnobattleonly_switch.get())
        if itemnobattleonly_switch.get() == "False":
            nobattleonly = False
        items[new_name] = {"rarity": new_rarity, "price": new_price, "consumable": consumable, "statuseffect": statuseffect, "nobattleonly": nobattleonly, "description": new_description}
        if item != new_name:
            del items[item]
            itemlist.remove(item)
            itemlist.insert(0, new_name)
            item_select.configure(values=itemlist)
            selected_item.set(new_name)
        with lock and open('items.json', 'w') as f:
            json.dump(items, f, indent=2)
        
    def item_create_callback():
        itemname = itemname_entry.get()
        itemprice = float(itemprice_entry.get())
        rarity = itemrarity_select.get()
        description = itemdescription_textbox.get("0.0", "end")
        if "" in (itemname, itemprice, description) or itemname in items:
            return
        consumable = bool(itemconsumable_switch.get())
        if itemconsumable_switch.get() == "False":
            consumable = False
        statuseffect = bool(itemstatuseffect_switch.get())
        if itemstatuseffect_switch.get() == "False":
            statuseffect = False
        nobattleonly = bool(itemnobattleonly_switch.get())
        if itemnobattleonly_switch.get() == "False":
            nobattleonly = False
        items[itemname] = {"rarity": rarity, "price": itemprice, "consumable": consumable, "statuseffect": statuseffect, "nobattleonly": nobattleonly, "description": description}
        with lock and open('items.json', 'w') as f:
            json.dump(items, f, indent=2)
        itemlist.insert(0, itemname)
        item_select.configure(values=itemlist)
        selected_item.set(itemname)
        item_select_callback(itemname)
        
    selected_item = ctk.StringVar(master=itab, value=itemlist[0])
    item_select = ctk.CTkOptionMenu(master=itab, values=itemlist, command=item_select_callback, variable=selected_item)
    item_select.grid(row=0, column=0, sticky='w')
    
    itemname_label = ctk.CTkLabel(master=itab, text="Name:")
    itemname_label.grid(row=1, column=0, sticky='w', pady=(10, 0))

    itemname_entry = ctk.CTkEntry(master=itab, textvariable=ctk.StringVar(master=itab, value=item_select.get()))
    itemname_entry.grid(row=2, column=0, sticky='w')

    selected_itemrarity = ctk.StringVar(master=itab, value=items[item_select.get()]['rarity'])
    itemrarity_label = ctk.CTkLabel(master=itab, text="Rarity:")
    itemrarity_label.grid(row=3, column=0, sticky='w', pady=(10,0))

    itemrarity_select = ctk.CTkOptionMenu(master=itab, values=itemrarity_list, variable=selected_itemrarity)
    itemrarity_select.grid(row=4, column=0, sticky='w')

    itemprice_label = ctk.CTkLabel(master=itab, text="Price:")
    itemprice_label.grid(row=5, column=0, sticky='w', pady=(10,0))

    itemprice_entry = ctk.CTkEntry(master=itab, validate="key", validatecommand=(valid_num, "%P"), textvariable=ctk.StringVar(master=itab, value=items[item_select.get()]['price']))
    itemprice_entry.grid(row=6, column=0, sticky='w')

    itemconsumable_label = ctk.CTkLabel(master=itab, text="Consumable:")
    itemconsumable_label.grid(row=7, column=0, sticky='w', pady=(10,0))

    itemconsumable = ctk.StringVar(master=itab, value=str(items[item_select.get()]['consumable']))
    itemconsumable_switch = ctk.CTkSwitch(master=itab, text="", command=itemconsumable_switch_callback, variable=itemconsumable, onvalue='True', offvalue='False')
    itemconsumable_switch.grid(row=7, column=1, sticky='w', pady=(10,0))

    itemstatuseffect_label = ctk.CTkLabel(master=itab, text="Status Effect:")
    itemstatuseffect_label.grid(row=8, column=0, sticky='w', pady=(10,0))

    itemstatuseffect = ctk.StringVar(master=itab, value=str(items[item_select.get()]['statuseffect']))
    itemstatuseffect_switch = ctk.CTkSwitch(master=itab, text="", command=itemstatuseffect_switch_callback, variable=itemstatuseffect, onvalue="True", offvalue="False")
    itemstatuseffect_switch.grid(row=8, column=1, sticky='w')

    itemnobattleonly_label = ctk.CTkLabel(master=itab, text="No Battle Only:")
    itemnobattleonly_label.grid(row=9, column=0, sticky='w', pady=(10,0))

    itemnobattleonly = ctk.StringVar(master=itab, value=str(items[item_select.get()]['nobattleonly']))
    itemnobattleonly_switch = ctk.CTkSwitch(master=itab, text="", command=itemnobattleonly_switch_callback, variable=itemnobattleonly, onvalue="True", offvalue="False")
    itemnobattleonly_switch.grid(row=9, column=1, sticky='w')

    itemdescription_label = ctk.CTkLabel(master=itab, text="Description:")
    itemdescription_label.grid(row=10, column=0, sticky='w', pady=(10,0))

    itemdescription = items[item_select.get()]['description']
    itemdescription_textbox = ctk.CTkTextbox(master=itab)
    itemdescription_textbox.insert("0.0", itemdescription)
    itemdescription_textbox.grid(row=11, column=0, columnspan=2, sticky='ew')

    item_save_or_create = ctk.CTkButton(master=itab, text="Save Changes", command=item_save_callback)
    item_save_or_create.grid(row=12, column=0, pady=(10,0), sticky='w')

    #boss editor-----------------------------------------------------------------------------------------

    bosskey_list = [key for key in items if items[key]['rarity'] == 'Key-Item']
    bossstat_label_dict = {}
    bossstat_entry_dict = {}
    bossskills_label_dict = {}
    bossskills_del_dict = {}

    def boss_select_callback(boss):
        global bossskills_list
        if boss == "new":
            bossname_entry.configure(textvariable=ctk.StringVar(master=btab_scroll, value=''))
            selected_bosstype.set("Fire")
            selected_bossbanner.set('Normal')
            selected_bosskey.set('Test Key')
            bosslvl_entry.configure(textvariable=ctk.StringVar(master=btab_scroll, value=""))
            bosshp_entry.configure(textvariable=ctk.StringVar(master=btab_scroll, value=""))
            bossdescription_textbox.delete('0.0', 'end')
            bossentrance_text.delete("0.0", 'end')
            bossmonumentname_entry.configure(textvariable=ctk.StringVar(master=btab_scroll, value=""))
            bossmonumentdescription_text.delete('0.0', 'end')
            bossskills_list.clear()
            render_bossskills()
            for stat in stat_list:
                bossstat_entry_dict[stat].configure(textvariable=ctk.StringVar(master=btab_scroll, value=""))
            boss_create_save.configure(text="Create Boss")
            boss_create_save.configure(command=boss_create_callback)
        else:
            bossname_entry.configure(textvariable=ctk.StringVar(master=btab_scroll, value=boss))
            selected_bosstype.set(bosses[boss]['type'])
            selected_bossbanner.set(bosses[boss]['banner'])
            selected_bosskey.set(bosses[boss]['key'])
            bosslvl_entry.configure(textvariable=ctk.StringVar(master=btab_scroll, value=str(bosses[boss]['lvl'])))
            bosshp_entry.configure(textvariable=ctk.StringVar(master=btab_scroll, value=str(bosses[boss]['maxhp'])))
            bossdescription_textbox.delete('0.0', 'end')
            bossdescription_textbox.insert('0.0', bosses[boss]['description'])
            bossentrance_text.delete('0.0', 'end')
            bossentrance_text.insert('0.0', bosses[boss]['entrancemsg'])
            bossmonumentname_entry.configure(textvariable=ctk.StringVar(master=btab_scroll, value=list(bosses[boss]['monument'].keys())[0]))
            bossmonumentdescription_text.delete('0.0', 'end')
            bossmonumentdescription_text.insert('0.0', bosses[boss]['monument'][bossmonumentname_entry.get()]['description'])
            bossskills_list.clear()
            bossskills_list.extend([skill for skill in bosses[boss]['skills']])
            render_bossskills()
            for stat in stat_list:
                bossstat_entry_dict[stat].configure(textvariable=ctk.StringVar(master=btab_scroll, value=bosses[boss]['stats'][stat]))
            boss_create_save.configure(text="Save Changes")
            boss_create_save.configure(command=boss_save_callback)

    def boss_save_callback():
        boss = boss_select.get()
        new_bossname = bossname_entry.get()
        if (boss != new_bossname and new_bossname in bosses) or len(bossskills_list) == 0:
            return
        new_bosslvl = int(bosslvl_entry.get())
        new_bosshp = int(bosshp_entry.get())
        new_bossdescription = bossdescription_textbox.get('0.0', 'end')
        new_bossentrance = bossentrance_text.get('0.0', 'end')
        new_bossmonumentname = bossmonumentname_entry.get()
        new_bossmonumentdescription = bossmonumentdescription_text.get('0.0', 'end')
        if "" in (new_bossname, new_bosslvl, new_bosshp, new_bossdescription, new_bossentrance, new_bossmonumentname, new_bossmonumentdescription):
            return
        bosses[new_bossname] = {'rarity': 'Incandescent', 'banner': bossbanner_select.get(), 'type': bosstype_select.get(), 'key': bosskey_select.get(), 'lvl': new_bosslvl, 'maxhp': new_bosshp, 'currhp': new_bosshp, 'monuments': {new_bossmonumentname: {'rarity': 'Monument', 'banner': bossbanner_select.get(), 'description': new_bossmonumentdescription}}, 'stats': {stat: bossstat_entry_dict[stat].get() for stat in stat_list}, 'description': new_bossdescription, 'entrancemsg': new_bossentrance, 'statuses': [], 'skills': {skill: skills[skill] for skill in bossskills_list}}
        for skill in bossskills_list:
            bosses[new_bossname]['skills'][skill]['equiped'] = True
        if boss != new_bossname:
            del bosses[boss]
            bosslist.remove(boss)
            bosslist.insert(0, new_bossname)
            boss_select.configure(values=bosslist)
            selected_boss.set(new_bossname)
        with lock and open('boss-mons.json', 'w') as f:
            json.dump(bosses, f, indent=2)

    def boss_create_callback():
        bossname = bossname_entry.get()
        bosslvl = int(bosslvl_entry.get())
        bosshp = int(bosshp_entry.get())
        bossdescription = bossdescription_textbox.get('0.0', 'end')
        bossentrance = bossentrance_text.get('0.0', 'end')
        bossmonumentname = bossmonumentname_entry.get()
        bossmonumentdescription = bossmonumentdescription_text.get('0.0', 'end')
        if "" in (bossname, bosslvl, bosshp, bossdescription, bossentrance, bossmonumentname, bossmonumentdescription) or bossname in bosses or len(bossskills_list) == 0:
            return
        bosses[bossname] = {'rarity': "Incandescent", 'banner': bossbanner_select.get(), 'type': bosstype_select.get(), 'key': bosskey_select.get(), 'lvl': bosslvl, 'maxhp': bosshp, 'currhp': bosshp, 'stats': {stat: bossstat_entry_dict[stat].get() for stat in stat_list}, 'description': bossdescription, 'entrancemsg': bossentrance, 'statuses': [], 'skills': {skill: skills[skill] for skill in bossskills_list}}
        bosses[bossname]['monument'] = {bossmonumentname: {'rarity': 'Monument', 'banner': bossbanner_select.get(), 'description': bossmonumentdescription}}
        for skill in bossskills_list:
            bosses[bossname]['skills'][skill]['equiped'] = True
        with lock and open('boss-mons.json', 'w') as f:
            json.dump(bosses, f, indent=2)
        bosslist.insert(0, bossname)
        boss_select.configure(values=bosslist)
        selected_boss.set(bossname)
        boss_select_callback(bossname)

    selected_boss = ctk.StringVar(master=btab_scroll, value=bosslist[0])
    boss_select = ctk.CTkOptionMenu(master=btab_scroll, values=bosslist, variable=selected_boss, command=boss_select_callback)
    boss_select.grid(row=0, column=0, sticky='w')

    bossname_label = ctk.CTkLabel(master=btab_scroll, text="Name:")
    bossname_label.grid(row=1, column=0, sticky='w', pady=(10,0))

    bossname_entry = ctk.CTkEntry(master=btab_scroll, textvariable=ctk.StringVar(master=btab_scroll, value=boss_select.get()))
    bossname_entry.grid(row=2, column=0, sticky='w')

    bosstype_label = ctk.CTkLabel(master=btab_scroll, text="Type:")
    bosstype_label.grid(row=3, column=0, sticky='w', pady=(10,0))

    selected_bosstype = ctk.StringVar(master=btab_scroll, value=bosses[boss_select.get()]['type'])
    bosstype_select = ctk.CTkOptionMenu(master=btab_scroll, values=list(typings.keys()), variable=selected_bosstype)
    bosstype_select.grid(row=4, column=0, sticky='w')

    bossbanner_label = ctk.CTkLabel(master=btab_scroll, text="Banner:")
    bossbanner_label.grid(row=5, column=0, sticky='w', pady=(10,0))

    selected_bossbanner = ctk.StringVar(master=btab_scroll, value=bosses[boss_select.get()]['banner'])
    bossbanner_select = ctk.CTkOptionMenu(master=btab_scroll, values=usebanner_list, variable=selected_bossbanner)
    bossbanner_select.grid(row=6, column=0, sticky='w')

    bosskey_label = ctk.CTkLabel(master=btab_scroll, text='Key:')
    bosskey_label.grid(row=7, column=0, sticky='w', pady=(10,0))

    selected_bosskey = ctk.StringVar(master=btab_scroll, value=bosses[boss_select.get()]['key'])
    bosskey_select = ctk.CTkOptionMenu(master=btab_scroll, values=bosskey_list, variable=selected_bosskey)
    bosskey_select.grid(row=8, column=0, sticky='w')

    bosslvl_label = ctk.CTkLabel(master=btab_scroll, text="lvl:")
    bosslvl_label.grid(row=9, column=0, sticky='w', pady=(10,0))

    bosslvl_entry = ctk.CTkEntry(master=btab_scroll, validate="key", validatecommand=(valid_num, "%P"), textvariable=ctk.StringVar(master=btab_scroll, value=str(bosses[boss_select.get()]['lvl'])))
    bosslvl_entry.grid(row=10, column=0, sticky='w')

    bosshp_label = ctk.CTkLabel(master=btab_scroll, text="Hp")
    bosshp_label.grid(row=12, column=0, sticky='w', pady=(10,0))

    bosshp_entry = ctk.CTkEntry(master=btab_scroll, validate="key", validatecommand=(valid_num, "%P"), textvariable=ctk.StringVar(master=btab_scroll, value=str(bosses[boss_select.get()]['maxhp'])))
    bosshp_entry.grid(row=13, column=0, sticky='w')

    bossdescription_label = ctk.CTkLabel(master=btab_scroll, text="Description:")
    bossdescription_label.grid(row=14, column=0, sticky='w', pady=(10,0))

    bossdescription = bosses[boss_select.get()]['description']
    bossdescription_textbox = ctk.CTkTextbox(master=btab_scroll)
    bossdescription_textbox.insert('0.0', bossdescription)
    bossdescription_textbox.grid(row=15, column=0, columnspan=2, sticky='ew')

    bossentrance_label = ctk.CTkLabel(master=btab_scroll, text="Entrance Message:")
    bossentrance_label.grid(row=16, column=0, sticky='w', pady=(10,0))

    bossentrance = bosses[boss_select.get()]['entrancemsg']
    bossentrance_text = ctk.CTkTextbox(master=btab_scroll)
    bossentrance_text.insert('0.0', bossentrance)
    bossentrance_text.grid(row=17, column=0, sticky='ew')

    bossmonumentname_label = ctk.CTkLabel(master=btab_scroll, text='Monument Name:')
    bossmonumentname_label.grid(row=18, column=0, sticky='w', pady=(10,0))

    bossmonumentname_entry = ctk.CTkEntry(master=btab_scroll, textvariable=ctk.StringVar(master=btab_scroll, value=list(bosses[boss_select.get()]['monument'].keys())[0]))
    bossmonumentname_entry.grid(row=19, column=0, sticky='w')

    bossmonumentdescription_label = ctk.CTkLabel(master=btab_scroll, text="Monument Description")
    bossmonumentdescription_label.grid(row=20, column=0, sticky='w', pady=(10,0))

    bossmonumentdescription = bosses[boss_select.get()]['monument'][list(bosses[boss_select.get()]['monument'].keys())[0]]['description']
    bossmonumentdescription_text = ctk.CTkTextbox(master=btab_scroll)
    bossmonumentdescription_text.insert('0.0', bossmonumentdescription)
    bossmonumentdescription_text.grid(row=21, column=0, sticky='ew')

    global bossskills_list
    bossskills_list = [skill for skill in bosses[boss_select.get()]['skills']]

    def bossskill_select_callback(skill):
        if skill in bossskills_list or len(bossskills_list) == 4:
            return
        bossskills_list.append(skill)
        render_bossskills()

    def bossskills_del_callback(skill):
        bossskills_list.remove(skill)
        render_bossskills()

    bossskills_label = ctk.CTkLabel(master=btab_scroll, text='Skills:')
    bossskills_label.grid(row=22, column=0, sticky='w', pady=(10,0))

    selected_bossskill = ctk.StringVar(master=btab_scroll, value=list(skills.keys())[0])
    bossskill_select = ctk.CTkOptionMenu(master=btab_scroll, values=list(skills.keys()), variable=selected_bossskill, command=bossskill_select_callback)
    bossskill_select.grid(row=22, column=1, sticky='w', pady=(10, 0))

    bossskills_scroll = ctk.CTkScrollableFrame(master=btab_scroll)
    bossskills_scroll.grid(row=23, column=0, columnspan=2, sticky='nsew')
    bossskills_scroll.grid_columnconfigure((0,1), weight=1)

    def render_bossskills():
        for skill in bossskills_label_dict:
            bossskills_label_dict[skill].destroy()
        bossskills_label_dict.clear()
        for skill in bossskills_del_dict:
            bossskills_del_dict[skill].destroy()
        bossskills_del_dict.clear()
        row = 0
        for skill in bossskills_list:
            bossskills_label_dict[skill] = ctk.CTkLabel(master=bossskills_scroll, text=f'{skill}:')
            bossskills_label_dict[skill].grid(row=row, column=0, sticky='w', pady=(10,0))

            bossskills_del_dict[skill] = ctk.CTkButton(master=bossskills_scroll, text='Delete', fg_color='red', command=lambda s=skill: bossskills_del_callback(s))
            bossskills_del_dict[skill].grid(row=row, column=1, sticky='w', pady=(10,0))

            row += 1
    render_bossskills()

    bossrow = 24
    for stat in stat_list:
        bossstat_label_dict[stat] = ctk.CTkLabel(master=btab_scroll, text=f"{stat}:")
        bossstat_label_dict[stat].grid(row=bossrow, column=0, sticky='w', pady=(10,0))

        bossstat_entry_dict[stat] = ctk.CTkEntry(master=btab_scroll, validate="key", validatecommand=(valid_num, "%P"), textvariable=ctk.StringVar(master=btab_scroll, value=str(bosses[boss_select.get()]['stats'][stat])))
        bossstat_entry_dict[stat].grid(row=bossrow, column=1, sticky='w', pady=(10,0))

        bossrow += 1

    bossrow+=1
    boss_create_save = ctk.CTkButton(master=btab_scroll, text="Save Changes", command=boss_save_callback)
    boss_create_save.grid(row=bossrow, column=0, sticky='w', pady=(10,0))

    #banner editor------------------------------------------------------------------------------------------

    bannerrarity_list = ['Common', 'Uncommon', 'Rare', 'Legendary', 'Incandescent']
    bannerdrop_labels = {}
    bannerdrop_del_buttons = {}
    bannerdrop_list = [drop for drop in banners[bannerlist[0]]['drop-pool'] if drop != "none"]

    def banner_select_callback(banner):
        if banner == "new":
            bannername_entry.configure(textvariable=ctk.StringVar(master=bantab, value=""))
            selected_bannerrarity.set("Common")
            bannerlvllow_entry.configure(textvariable=ctk.StringVar(master=bantab, value=""))
            bannerlvlhigh_entry.configure(textvariable=ctk.StringVar(master=bantab, value=""))
            bannerdescription_textbox.delete('0.0', 'end')
            bannerdrop_list.clear()
            render_droplist()
            banner_save_create.configure(text="Create Banner")
            banner_save_create.configure(command=banner_create_callback)
        else:
            bannername_entry.configure(textvariable=ctk.StringVar(master=bantab, value=banner))
            selected_bannerrarity.set(banners[banner]['rarity'])
            bannerlvllow_entry.configure(textvariable=ctk.StringVar(master=bantab, value=str(min(banners[banner]['lvlweights']))))
            bannerlvlhigh_entry.configure(textvariable=ctk.StringVar(master=bantab, value=str(max(banners[banner]['lvlweights']))))
            bannerdescription_textbox.delete('0.0', 'end')
            bannerdescription_textbox.insert('0.0', banners[banner]['description'])
            bannerdrop_list.clear()
            bannerdrop_list.extend([drop for drop in banners[banner]['drop-pool'] if drop != 'none'])
            render_droplist()
            banner_save_create.configure(text="Save Changes")
            banner_save_create.configure(command=banner_save_callback)

    def bannerdrop_select_callback(drop):
        if drop in bannerdrop_list:
            return
        bannerdrop_list.append(drop)
        render_droplist()

    def bannerdrop_del_callback(item):
        bannerdrop_list.remove(item)
        render_droplist()

    def banner_save_callback():
        banner = banner_select.get()
        newbannername = bannername_entry.get()
        if newbannername != banner and newbannername in banners:
            return
        newlvllow = int(bannerlvllow_entry.get())
        newlvlhigh = int(bannerlvlhigh_entry.get())
        newbannerdescription = bannerdescription_textbox.get('0.0', 'end')
        if "" in (newbannername, newlvllow, newlvlhigh, newbannerdescription):
            return
        new_drop_pool = {drop: items[drop] for drop in bannerdrop_list}
        new_drop_pool["none"] = 'none'
        banners[newbannername] = {"rarity": bannerrarity_select.get(), "description": newbannerdescription, "lvlweights": [newlvllow, newlvlhigh], "drop-pool": new_drop_pool}
        if newbannername != banner:
            del banners[banner]
            bannerlist.remove(banner)
            bannerlist.insert(0, newbannername)
            banner_select.configure(values=bannerlist)
            selected_banner.set(newbannername)
        with lock and open('banners.json', 'w') as f:
            json.dump(banners, f, indent=2)

    def banner_create_callback():
        bannername = bannername_entry.get()
        lvllow = int(bannerlvllow_entry.get())
        lvlhigh = int(bannerlvlhigh_entry.get())
        description = bannerdescription_textbox.get('0.0', 'end')
        if "" in (bannername, lvllow, lvlhigh, description) or bannername in banners:
            return
        drop_pool = {drop: items[drop] for drop in bannerdrop_list}
        drop_pool['none'] = 'none'
        banners[bannername] = {'rarity': bannerrarity_select.get(), 'description': description, 'lvlweights': [lvllow, lvlhigh], 'drop-pool': drop_pool}
        with lock and open('banners.json', 'w') as f:
            json.dump(banners, f, indent=2)
        bannerlist.insert(0, bannername)
        banner_select.configure(values=bannerlist)
        selected_banner.set(bannername)
        banner_select_callback(bannername)

    selected_banner = ctk.StringVar(master=bantab, value=bannerlist[0])
    banner_select = ctk.CTkOptionMenu(master=bantab, values=bannerlist, variable=selected_banner, command=banner_select_callback)
    banner_select.grid(row=0, column=0, sticky='w')

    bannername_label = ctk.CTkLabel(master=bantab, text="Name:")
    bannername_label.grid(row=1, column=0, sticky='w', pady=(10,0))

    bannername_entry = ctk.CTkEntry(master=bantab, textvariable=ctk.StringVar(master=bantab, value=banner_select.get()))
    bannername_entry.grid(row=2, column=0, sticky='w')

    bannerrarity_label = ctk.CTkLabel(master=bantab, text="Rarity:")
    bannerrarity_label.grid(row=3, column=0, sticky='w', pady=(10,0))

    selected_bannerrarity = ctk.StringVar(master=bantab, value=banners[banner_select.get()]['rarity'])
    bannerrarity_select = ctk.CTkOptionMenu(master=bantab, values=bannerrarity_list, variable=selected_bannerrarity)
    bannerrarity_select.grid(row=4, column=0, sticky='w')

    bannerlvllow_label = ctk.CTkLabel(master=bantab, text="lvl below user lvl:")
    bannerlvllow_label.grid(row=5, column=0, sticky='w', pady=(10,0))

    bannerlvllow_entry = ctk.CTkEntry(master=bantab, validate="key", validatecommand=(valid_num, "%P"), textvariable=ctk.StringVar(master=bantab, value=str(min(banners[banner_select.get()]['lvlweights']))))
    bannerlvllow_entry.grid(row=6, column=0, sticky='w')

    bannerlvlhigh_label = ctk.CTkLabel(master=bantab, text="lvl above user lvl:")
    bannerlvlhigh_label.grid(row=5, column=1, sticky='w', pady=(10,0))

    bannerlvlhigh_entry = ctk.CTkEntry(master=bantab, validate="key", validatecommand=(valid_num, "%P"), textvariable=ctk.StringVar(master=bantab, value=str(max(banners[banner_select.get()]['lvlweights']))))
    bannerlvlhigh_entry.grid(row=6, column=1, sticky='w')

    bannerdescription_label = ctk.CTkLabel(master=bantab, text='Description:')
    bannerdescription_label.grid(row=7, column=0, sticky='w', pady=(10,0))

    bannerdescription = banners[banner_select.get()]['description']
    bannerdescription_textbox = ctk.CTkTextbox(master=bantab)
    bannerdescription_textbox.insert('0.0', bannerdescription)
    bannerdescription_textbox.grid(row=8, column=0, columnspan=2, sticky='w')

    bannerdrop_label = ctk.CTkLabel(master=bantab, text='Drop Pool:')
    bannerdrop_label.grid(row=9, column=0, sticky='w', pady=(10,0))

    selected_bannerdrop = ctk.StringVar(master=bantab, value=list(items.keys())[0])
    bannerdrop_select = ctk.CTkOptionMenu(master=bantab, values=list(items.keys()), variable=selected_bannerdrop, command=bannerdrop_select_callback)
    bannerdrop_select.grid(row=9, column=1, sticky='w', pady=(10,0))

    bannerdrop_scroll = ctk.CTkScrollableFrame(master=bantab)
    bannerdrop_scroll.grid(row=10, column=0, columnspan=2, sticky='nsew')
    bannerdrop_scroll.grid_columnconfigure((0,1,), weight=1)

    def render_droplist():
        bannerrowct = 1
        for label in bannerdrop_labels:
            bannerdrop_labels[label].destroy()
        bannerdrop_labels.clear()
        for button in bannerdrop_del_buttons:
            bannerdrop_del_buttons[button].destroy()
        bannerdrop_del_buttons.clear()
        for item in bannerdrop_list:
            bannerdrop_labels[item] = ctk.CTkLabel(master=bannerdrop_scroll, text=f"{item}:")
            bannerdrop_labels[item].grid(row=bannerrowct, column=0, sticky='w', pady=(10,0))

            bannerdrop_del_buttons[item] = ctk.CTkButton(master=bannerdrop_scroll, text='Remove', fg_color='red', command=lambda item=item: bannerdrop_del_callback(item))
            bannerdrop_del_buttons[item].grid(row=bannerrowct, column=1, sticky='w', pady=(10,0))

            bannerrowct += 1
    render_droplist()

    banner_save_create = ctk.CTkButton(master=bantab, text="Save Changes", command=banner_save_callback)
    banner_save_create.grid(row=11, column=0, sticky='w', pady=(10,0))

    #stock editor---------------------------------------------------------------------

    def stock_select_callback(stock):
        if stock == "new":
            stockname_entry.configure(textvariable=ctk.StringVar(master=stotab, value=""))
            stockprice_entry.configure(textvariable=ctk.StringVar(master=stotab, value=""))
            stock_save_or_create.configure(text="Create New")
            stock_save_or_create.configure(command=stock_create_callback)
        else:
            stockname_entry.configure(textvariable=ctk.StringVar(master=stotab, value=stock))
            stockprice_entry.configure(textvariable=ctk.StringVar(master=stotab, value=str(stocks[stock]['price'])))
            stock_save_or_create.configure(text="Save Changes")
            stock_save_or_create.configure(command=stock_save_callback)

    def stock_save_callback():
        stock = stock_select.get()
        new_name = stockname_entry.get()
        if new_name != stock and new_name in stocks:
            return
        new_price = float(stockprice_entry.get())
        if "" in (new_name, new_price):
            return
        stocks[new_name] = {"price": new_price, "favorlvl": stocks[stock]['favorlvl']}
        if stock != new_name:
            del stocks[stock]
            stocklist.remove(stock)
            stocklist.insert(0, new_name)
            stock_select.configure(values=stocklist)
            selected_stock.set(new_name)
        with lock and open('stocks.json', 'w') as f:
            json.dump(stocks, f, indent=2)

    def stock_create_callback():
        stockname = stockname_entry.get()
        stockprice = float(stockprice_entry.get())
        if "" in (stockname, stockprice) or stockname in stocks:
            return
        stocks[stockname] = {"price": stockprice, "favorlvl": "none"}
        with lock and open('stocks.json', 'w') as f:
            json.dump(stocks, f, indent=2)
        stocklist.insert(0, stockname)
        stock_select.configure(values=stocklist)
        selected_stock.set(stockname)
        stock_select_callback(stockname)

    selected_stock = ctk.StringVar(value=stocklist[0])
    stock_select = ctk.CTkOptionMenu(master=stotab, values=stocklist, command=stock_select_callback, variable=selected_stock)
    stock_select.grid(row=0, column=0, sticky='w')

    stockname_label = ctk.CTkLabel(master=stotab, text="Name:")
    stockname_label.grid(row=1, column=0, sticky='w', pady=(10, 0))

    stockname_entry = ctk.CTkEntry(master=stotab, textvariable=ctk.StringVar(master=stotab, value=stock_select.get()))
    stockname_entry.grid(row=2, column=0)

    stockprice_label = ctk.CTkLabel(master=stotab, text="Price:")
    stockprice_label.grid(row=3, column=0, sticky='w', pady=(10, 0))

    stockprice_entry = ctk.CTkEntry(master=stotab, validate="key", validatecommand=(valid_num, "%P"), textvariable=ctk.StringVar(master=stotab, value=str(stocks[stock_select.get()]['price'])))
    stockprice_entry.grid(row=4, column=0)

    stock_save_or_create = ctk.CTkButton(master=stotab, text="Save Changes", command=stock_save_callback)
    stock_save_or_create.grid(row=5, column=0, pady=(20,0))

    #typing editor-----------------------------------------------------------------------------------------------

    typeweak_list = [mtype for mtype in typings[typelist[0]] if typings[typelist[0]][mtype] == 1.3]
    typeweak_label_dict = {}
    typeweak_del_dict ={}
    typestrong_list = [mtype for mtype in typings[typelist[0]] if typings[typelist[0]][mtype] == 0.7]
    typestrong_label_dict = {}
    typestrong_del_dict ={}
    typedefenseless_list = [mtype for mtype in typings[typelist[0]] if typings[typelist[0]][mtype] == 1.7]
    typedefenseless_label_dict = {}
    typedefenseless_del_dict ={}
    typeimmune_list = [mtype for mtype in typings[typelist[0]] if typings[typelist[0]][mtype] == 0.3]
    typeimmune_label_dict = {}
    typeimmune_del_dict ={}

    def type_select_callback(mtype):
        if mtype == "new":
            typename_entry.configure(textvariable=ctk.StringVar(master=ttab, value=""))
            typeweak_list.clear()
            render_typeweak_scroll()
            typestrong_list.clear()
            render_typestrong_scroll()
            typedefenseless_list.clear()
            render_typedefenseless_scroll()
            typeimmune_list.clear()
            render_typeimmune_scroll()
            type_save_create.configure(text='Create Type')
            type_save_create.configure(command=type_create_callback)
        else:
            typename_entry.configure(textvariable=ctk.StringVar(master=ttab, value=type_select.get()))
            typeweak_list.clear()
            typeweak_list.extend([montype for montype in typings[mtype] if typings[mtype][montype] == 1.3])
            render_typeweak_scroll()
            typestrong_list.clear()
            typestrong_list.extend([montype for montype in typings[mtype] if typings[mtype][montype] == 0.7])
            render_typestrong_scroll()
            typedefenseless_list.clear()
            typedefenseless_list.extend([montype for montype in typings[mtype] if typings[mtype][montype] == 1.7])
            render_typedefenseless_scroll()
            typeimmune_list.clear()
            typeimmune_list.extend([montype for montype in typings[mtype] if typings[mtype][montype] == 0.3])
            render_typeimmune_scroll()
            type_save_create.configure(text="Save Changes")
            type_save_create.configure(command=type_save_callback)

    def typeweak_select_callback(mtype):
        if any(mtype in sublist for sublist in [typeweak_list, typestrong_list, typedefenseless_list, typeimmune_list]):
            return
        typeweak_list.append(mtype)
        render_typeweak_scroll()

    def typestrong_select_callback(mtype):
        if any(mtype in sublist for sublist in [typeweak_list, typestrong_list, typedefenseless_list, typeimmune_list]):
            return
        typestrong_list.append(mtype)
        render_typestrong_scroll()

    def typedefenseless_select_callback(mtype):
        if any(mtype in sublist for sublist in [typeweak_list, typestrong_list, typedefenseless_list, typeimmune_list]):
            return
        typedefenseless_list.append(mtype)
        render_typedefenseless_scroll()

    def typeimmune_select_callback(mtype):
        if any(mtype in sublist for sublist in [typeweak_list, typestrong_list, typedefenseless_list, typeimmune_list]):
            return
        typeimmune_list.append(mtype)
        render_typeimmune_scroll()

    def typeweak_del_callback(mtype):
        typeweak_list.remove(mtype)
        render_typeweak_scroll()

    def typestrong_del_callback(mtype):
        typestrong_list.remove(mtype)
        render_typestrong_scroll()

    def typedefenseless_del_callback(mtype):
        typedefenseless_list.remove(mtype)
        render_typedefenseless_scroll()

    def typeimmune_del_callback(mtype):
        typeimmune_list().remove(mtype)
        render_typeimmune_scroll()

    def type_save_callback():
        typename = type_select.get()
        newtype_name = typename_entry.get()
        if (typename != newtype_name and newtype_name in typings) or newtype_name == "":
            return
        for mtype in typeweak_list:
            if newtype_name not in typings:
                typings[newtype_name] = {}
            typings[newtype_name][mtype] = 1.3
        for mtype in typestrong_list:
            if newtype_name not in typings:
                typings[newtype_name] = {}
            typings[newtype_name][mtype] = 0.7
        for mtype in typedefenseless_list:
            if newtype_name not in typings:
                typings[newtype_name] = {}
            typings[newtype_name][mtype] = 1.7
        for mtype in typeimmune_list:
            if newtype_name not in typings:
                typings[newtype_name] = {}
            typings[newtype_name][mtype] = 0.3
        if newtype_name != typename:
            del typings[typename]
            typelist.remove(typename)
            typelist.insert(0, newtype_name)
            type_select.configure(values=typelist)
            selected_type.set(newtype_name)
        with lock and open('typing.json', 'w') as f:
            json.dump(typings, f, indent=2)

    def type_create_callback():
        typename = typename_entry.get()
        if typename == "":
            return
        for mtype in typeweak_list:
            if typename not in typings:
                typings[typename] = {}
            typings[typename][mtype] = 1.3
        for mtype in typestrong_list:
            if typename not in typings:
                typings[typename] = {}
            typings[typename][mtype] = 0.7
        for mtype in typedefenseless_list:
            if typename not in typings:
                typings[typename] = {}
            typings[typename][mtype] = 1.7
        for mtype in typeimmune_list:
            if typename not in typings:
                typings[typename] = {}
            typings[typename][mtype] = 0.3
        with lock and open('typing.json', 'w') as f:
            json.dump(typings, f, indent=2)
        typelist.insert(0, typename)
        type_select.configure(values=typelist)
        selected_type.set(typename)
        type_select_callback(typename)

    selected_type = ctk.StringVar(master=ttab, value=typelist[0])
    type_select = ctk.CTkOptionMenu(master=ttab, values=typelist, variable=selected_type, command=type_select_callback)
    type_select.grid(row=0, column=0, sticky='w')

    typename_label = ctk.CTkLabel(master=ttab, text='Name:')
    typename_label.grid(row=1, column=0, sticky='w', pady=(10,0))

    typename_entry = ctk.CTkEntry(master=ttab, textvariable=ctk.StringVar(master=ttab, value=type_select.get()))
    typename_entry.grid(row=2, column=0, sticky='w')

    typeweak_label = ctk.CTkLabel(master=ttab, text="Weak against:")
    typeweak_label.grid(row=3, column=0, sticky='w', pady=(10,0))

    selected_typeweak = ctk.StringVar(master=ttab, value=typelist[0])
    typeweak_select = ctk.CTkOptionMenu(master=ttab, values=list(typings.keys()), variable=selected_typeweak, command=typeweak_select_callback)
    typeweak_select.grid(row=3, column=1, sticky='w', pady=(10,0))

    typeweak_scroll = ctk.CTkScrollableFrame(master=ttab)
    typeweak_scroll.grid(row=4, column=0, columnspan=2, sticky='nsew')
    typeweak_scroll.grid_columnconfigure((0,1), weight=1)

    def render_typeweak_scroll():
        for mtype in typeweak_label_dict:
            typeweak_label_dict[mtype].destroy()
        typeweak_label_dict.clear()
        for mtype in typeweak_del_dict:
            typeweak_del_dict[mtype].destroy()
        typeweak_del_dict.clear()
        row = 0
        for mtype in typeweak_list:
            typeweak_label_dict[mtype] = ctk.CTkLabel(master=typeweak_scroll, text=f"{mtype}:")
            typeweak_label_dict[mtype].grid(row=row, column=0, sticky='w', pady=(10,0))

            typeweak_del_dict[mtype] = ctk.CTkButton(master=typeweak_scroll, text="Delete", command=lambda t=mtype: typeweak_del_callback(t), fg_color="red")
            typeweak_del_dict[mtype].grid(row=row, column=1, sticky='w', pady=(10,0))

            row += 1
    render_typeweak_scroll()

    typestrong_label = ctk.CTkLabel(master=ttab, text="Strong against:")
    typestrong_label.grid(row=3, column=2, sticky='w', pady=(10,0), padx=10)

    selected_typestrong = ctk.StringVar(master=ttab, value=typelist[0])
    typestrong_select = ctk.CTkOptionMenu(master=ttab, values=list(typings.keys()), variable=selected_typestrong, command=typestrong_select_callback)
    typestrong_select.grid(row=3, column=3, sticky='w', pady=(10,0), padx=10)

    typestrong_scroll = ctk.CTkScrollableFrame(master=ttab)
    typestrong_scroll.grid(row=4, column=2, columnspan=2, sticky='nsew', padx=10)
    typestrong_scroll.grid_columnconfigure((0,1), weight=1)

    def render_typestrong_scroll():
        for mtype in typestrong_label_dict:
            typestrong_label_dict[mtype].destroy()
        typestrong_label_dict.clear()
        for mtype in typestrong_del_dict:
            typestrong_del_dict[mtype].destroy()
        typestrong_del_dict.clear()
        row = 0
        for mtype in typestrong_list:
            typestrong_label_dict[mtype] = ctk.CTkLabel(master=typestrong_scroll, text=f"{mtype}:")
            typestrong_label_dict[mtype].grid(row=row, column=0, sticky='w', pady=(10,0))

            typestrong_del_dict[mtype] = ctk.CTkButton(master=typestrong_scroll, text="Delete", command=lambda t=mtype: typestrong_del_callback(t), fg_color="red")
            typestrong_del_dict[mtype].grid(row=row, column=1, sticky='w', pady=(10,0))
    render_typestrong_scroll()

    typedefenseless_label = ctk.CTkLabel(master=ttab, text="Defenseless against:")
    typedefenseless_label.grid(row=5, column=0, sticky='w', pady=(10,0))

    selected_typedefenseless = ctk.StringVar(master=ttab, value=typelist[0])
    typedefenseless_select = ctk.CTkOptionMenu(master=ttab, values=list(typings.keys()), variable=selected_typedefenseless, command=typedefenseless_select_callback)
    typedefenseless_select.grid(row=5, column=1, sticky='w', pady=(10,0))

    typedefenseless_scroll = ctk.CTkScrollableFrame(master=ttab)
    typedefenseless_scroll.grid(row=6, column=0, columnspan=2, sticky='nsew')
    typedefenseless_scroll.grid_columnconfigure((0,1), weight=1)

    def render_typedefenseless_scroll():
        for mtype in typedefenseless_label_dict:
            typedefenseless_label_dict[mtype].destroy()
        typedefenseless_label_dict.clear()
        for mtype in typedefenseless_del_dict:
            typedefenseless_del_dict[mtype].destroy()
        typedefenseless_del_dict.clear()
        row = 0
        for mtype in typedefenseless_list:
            typedefenseless_label_dict[mtype] = ctk.CTkLabel(master=typedefenseless_scroll, text=f'{mtype}:')
            typedefenseless_label_dict[mtype].grid(row=row, column=0, sticky='w', pady=(10,0))

            typedefenseless_del_dict[mtype] = ctk.CTkButton(master=typedefenseless_scroll, text='Delete', command=lambda t=mtype: typedefenseless_del_callback(t), fg_color="red")
            typedefenseless_del_dict[mtype].grid(row=row, column=1, sticky='w', pady=(10,0))

            row += 1
    render_typedefenseless_scroll()

    typeimmune_label = ctk.CTkLabel(master=ttab, text="Immune to:")
    typeimmune_label.grid(row=5, column=2, sticky='w', pady=(10,0), padx=10)

    selected_typeimmune = ctk.StringVar(master=ttab, value=typelist[0])
    typeimmune_select = ctk.CTkOptionMenu(master=ttab, values=list(typings.keys()), variable=selected_typeimmune, command=typeimmune_select_callback)
    typeimmune_select.grid(row=5, column=3, sticky='w', pady=(10,0), padx=10)

    typeimmune_scroll = ctk.CTkScrollableFrame(master=ttab)
    typeimmune_scroll.grid(row=6, column=2, columnspan=2, sticky='nsew', padx=10)
    typeimmune_scroll.grid_columnconfigure((0,1), weight=1)

    def render_typeimmune_scroll():
        for mtype in typeimmune_label_dict:
            typeimmune_label_dict[mtype].destroy()
        typeimmune_label_dict.clear()
        for mtype in typeimmune_del_dict:
            typeimmune_del_dict[mtype].destroy()
        typeimmune_del_dict.clear()
        row=0
        for mtype in typeimmune_list:
            typeimmune_label_dict[mtype] = ctk.CTkLabel(master=typeimmune_scroll, text=f'{mtype}:')
            typeimmune_label_dict[mtype].grid(row=row, column=0, sticky='w', pady=(10,0))

            typeimmune_del_dict[mtype] = ctk.CTkButton(master=typeimmune_scroll, text="Delete", command=lambda t=mtype: typeimmune_del_callback(t), fg_color="red")
            typeimmune_del_dict[mtype].grid(row=row, column=1, sticky='w', pady=(10,0))

            row += 1
    render_typeimmune_scroll()

    type_save_create = ctk.CTkButton(master=ttab, text='Save Changes', command=type_save_callback)
    type_save_create.grid(row=7, column=0, sticky='w', pady=(10,0))

    #running utility-----------------------------------------------------------------------------

    root.mainloop() 

if __name__ == "__main__":
    main()