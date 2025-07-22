import customtkinter as ctk
import numpy as np
import json
import asyncio
import re

lock = asyncio.Lock()

with lock and open('gricklemon.json') as f:
    mons = json.load(f)
with lock and open('skills.json') as f:
    skills = json.load(f)
with lock and open('items.json') as f:
    items = json.load(f)
with lock and open('boss-mons.json') as f:
    bossmons = json.load(f)
with lock and open('banners.json') as f:
    banners = json.load(f)
with lock and open('stocks.json') as f:
    stocks = json.load(f)

skilllist = list(skills.keys())
skilllist.append("new")
itemlist = list(items.keys())
itemlist.append("new")
stocklist = list(stocks.keys())
stocklist.append("new")

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

    #gricklemon editor-------------------------------------------------------------------------

    label_tab1 = ctk.CTkLabel(master=gtab, text="You're in Gricklemon Editor")
    label_tab1.grid(row=0, column=0)

    #skill editor---------------------------------------------------------------------------------------

    skillscaling_list = ["S", "A", "B", "C", "D", "E", "-"]
    skillstat_list = ['str', 'dex', 'int', 'fth', 'arc']
    skillbanner_list = list(banners.keys())
    skillbanner_list.remove('active')
    skillbanner_list.remove('change-date')
    skill_rarity = ['Common', 'Uncommon', 'Rare', 'Legendary', 'Incandescent']
    status_effects = ['Poison', 'Paralysis']
    skillstat_label_dict = {}
    skillstat_option_dict = {}
    skillstat_selected_dict={}
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
        new_skillbasedmg = skillbasedmg_entry.get()
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
        skillbasedmg = skillbasedmg_entry.get()
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
    skillbanner_select = ctk.CTkOptionMenu(master=stab, values=skillbanner_list, variable=selected_skillbanner)
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
        new_price = itemprice_entry.get()
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
        itemprice = itemprice_entry.get()
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



    #banner editor------------------------------------------------------------------------------------------



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
        stockprice = stockprice_entry.get()
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

    #running utility-----------------------------------------------------------------------------

    root.mainloop() 

if __name__ == "__main__":
    main()