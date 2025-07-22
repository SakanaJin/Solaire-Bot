import customtkinter as ctk
import numpy as np
import json
import asyncio
import re

lock = asyncio.Lock()

itemrarity_list = ['Common', 'Uncommon', 'Rare', 'Legendary', "Incandescent", 'Key-Item']

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



    #item editor------------------------------------------------------------------------------------------

    def item_select_callback(item):
        if item == "new":
            itemname_entry.configure(textvariable=ctk.StringVar(master=itab, value=""))
            selected_rarity.set("Common")
            itemprice_entry.configure(textvariable=ctk.StringVar(master=itab, value=""))
            itemconsumable_switch.deselect()
            itemstatuseffect_switch.deselect()
            itemnobattleonly_switch.deselect()
            itemdescription_textbox.delete("0.0", "end")
            item_save_or_create.configure(text="Create Item")
            item_save_or_create.configure(command=item_create_callback)
        else:
            itemname_entry.configure(textvariable=ctk.StringVar(master=itab, value=item))
            selected_rarity.set(items[item]['rarity'])
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

    selected_rarity = ctk.StringVar(master=itab, value=items[item_select.get()]['rarity'])
    itemrarity_label = ctk.CTkLabel(master=itab, text="Rarity:")
    itemrarity_label.grid(row=3, column=0, sticky='w', pady=(10,0))

    itemrarity_select = ctk.CTkOptionMenu(master=itab, values=itemrarity_list, variable=selected_rarity)
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