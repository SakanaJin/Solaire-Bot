import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import random
from random import SystemRandom
import requests
from bs4 import BeautifulSoup
import json
import datetime
import asyncio
import typing
from asteval import Interpreter

import grickle

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CID = os.getenv('CID')
GID = os.getenv('GID')
ADMIN: int = int(os.getenv('ADMIN'))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
general = None
guild = discord.Object(id=GID)

sysrand = SystemRandom()

headsortails = ["heads", "tails"]
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
solaire_quotes = [{"quote": "Praise the sun!", "author": "Solaire"}, {"quote": "If only I could be so grossly incandescent", "author": "Solaire"}, {"quote": "Oh, hello there. I will stay behind, to gaze at the sun. The sun is a wondrous body. Like a magnificent father", "author": "Solaire"}, {"quote": "You really are fond of chatting with me, aren't you? If I didn't know better, I'd think you had feelings for me! Ha ha ha", "author": "Solaire"}, {"quote": "I am Solaire of Astora, an adherent of the Lord of Sunlight. Now that I am Undead, I have come to this great land, the birthplace of Lord Gwyn, to seek my very own sun", "author": "Solaire"}, {"quote": "We are amidst strange beings, in a strange land. The flow of time itself is convoluted; with heroes centuries old phasing in and out", "author": "Solaire"}]
stock_favorlvls = ['hated', 'poor', 'none', 'favored', 'loved']
rarity_colors = {"Common": 0xf7faf8, "Uncommon": 0x14c744, "Rare": 0x1791e8, "Legendary": 0x7217e8, "Incandescent": 0xfcb632, "Key-Item": 0x068067, "Monument": 0xfcf914}
lock = asyncio.Lock()

#events-----------------------------------------------------------------------------------------------

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord")
    global general
    general = await bot.fetch_channel(CID)
    stock_check.start()
    birthday_check.start()
    shop_refresh.start()
    print(f"started tasks")

@bot.event
async def on_member_join(member):
    with lock and open('data.json') as f:
        data = json.load(f)
    data[member.id] = {"name": member.name, "birthday": "mm-dd", "fucks": 0, "sunlight": 100, "battleid": 0}
    with lock and open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await general.send(f"Welcome to the server {member.name}! Enjoying the sunlight?")

#tasks--------------------------------------------------------------------------------------------------

@tasks.loop(time=datetime.time(hour=15, minute=0)) #1500 utc 1000 cdt
async def birthday_check():
    with lock and open('data.json') as f:
        data = json.load(f)
    for userid in data:
        if data[userid]['birthday'] == str(datetime.date.today().strftime("%m-%d")):
            await general.send(f"Ahh, @everyone... Today is no ordinary day—it is a day of radiance! A day to honor you, a most noble and unwavering soul. Happy birthday, brave {data[userid]['name']}! With each passing year, your light grows stronger, shining boldly even through the deepest dark. May your journey ahead be filled with jolly cooperation, hearty laughter, and the warmth of the ever-glorious sun! So come—raise your arms high, and let us rejoice! Praise it! Praise the Sun! ☀️")

@tasks.loop(time=datetime.time(hour=17, minute=0)) #1700 utc 1200 cdt
async def stock_check():
    message = f"@everyone\nSunlight stock market report - {datetime.date.today()}\n"
    with open('stocks.json') as f: # might need a lock
        stocks = json.load(f)
    if datetime.date.today().weekday() in (0, 4): # monday and thursday
        for stock in stocks:
            stocks[stock]['favorlvl'] = random.choices(stock_favorlvls, weights=[5,25,40,25,5])[0]
    for stock in stocks:
        match stocks[stock]['favorlvl']:
            case 'hated':
                percent_change = sysrand.uniform(-0.20, 0.02)
            case 'poor':
                percent_change = sysrand.uniform(-0.05, 0.02)
            case 'neutral':
                percent_change = sysrand.uniform(-0.02, 0.05)
            case 'favored':
                percent_change = sysrand.uniform(-0.02, 0.15)
            case 'loved':
                percent_change = sysrand.uniform(-0.02, 0.20)
        stocks[stock]['price'] += stocks[stock]['price'] * percent_change
        stocks[stock]['price'] = round(stocks[stock]['price'], 2)
        sign = ""
        if percent_change > 0:
            sign = "+"
        message = message + f"{stock}: {stocks[stock]['price']} sunlight ({sign}{round(percent_change * 100, 2)}%)\n"
    with open('stocks.json', 'w') as f: # might need a lock
        json.dump(stocks, f, indent=2)
    await general.send(message)

@tasks.loop(time=datetime.time(hour=17, minute=30)) #1730 utc 1230 cdt
async def shop_refresh():
    with lock and open('items.json') as f:
        items = json.load(f)
    shop_items = {}
    #Populate shop with Incandescent items
    for _ in range(1):
        choices = [item for item in items if items[item]['rarity'] == 'Incandescent']
        chosen_one = random.choice(choices)
        shop_items[chosen_one] = items[chosen_one]
    #Populate shop with Legendary items
    for _ in range(1):
        choices = [item for item in items if items[item]['rarity'] == 'Legendary']
        chosen_one = random.choice(choices)
        shop_items[chosen_one] = items[chosen_one]
    #Populate shop with Rare items
    for _ in range(1):
        choices = [item for item in items if items[item]['rarity'] == 'Rare']
        chosen_one = random.choice(choices)
        shop_items[chosen_one] = items[chosen_one]
    #Populate shop with Uncommon items
    for _ in range(1):
        choices = [item for item in items if items[item]['rarity'] == 'Uncommon']
        chosen_one = random.choice(choices)
        shop_items[chosen_one] = items[chosen_one]
        #Populate shop with Common items
    for _ in range(1):
        choices = [item for item in items if items[item]['rarity'] == 'Common']
        chosen_one = random.choice(choices)
        shop_items[chosen_one] = items[chosen_one]
    with lock and open('shop.json', 'w') as f:
        json.dump(shop_items, f, indent=2)
    await general.send("@everyone\nShop has been refreshed.")

#on message---------------------------------------------------------------------------------------------

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    message = msg.content.lower()
    message = message.replace(" ", "")
    if "fuck" in message:
        await incfuck(msg.author)

    await bot.process_commands(msg)

async def incfuck(author):
    with lock and open('data.json') as f:
        data = json.load(f)
    data[str(author.id)]['fucks'] += 1
    with lock and open('data.json', 'w') as f:
        json.dump(data, f, indent=2)

#commands--------------------------------------------------------------------------------------------------

@bot.tree.command(guild=guild)
async def test(interaction):
    """:3"""
    await interaction.response.send_message(":3")

@bot.command()
async def sync(ctx):
    """syncs commands"""
    if ctx.author.id != ADMIN:
        await ctx.send("Admin only")
        return
    await bot.tree.sync(guild=guild)

@bot.command()
async def gsync(ctx):
    """global syncs commands"""
    if ctx.author.name != ADMIN:
        await ctx.send("Admin only")
        return
    await bot.tree.sync()

@bot.tree.command(guild=guild)
async def flip(interaction):
    """flips a coin"""
    await interaction.response.send_message(f"{headsortails[random.randint(0,1)]}")

@bot.tree.command(guild=guild)
async def rolld(interaction, sides: int = 6):
    """rolls blank sided die"""
    try:
        num = int(sides)
        await interaction.response.send_message(f"{random.randint(1,num)}")
    except Exception as e:
        await interaction.response.send_message(f"{e}")

@bot.tree.command(guild=guild)
async def meme(interaction):
    """funee"""
    response = requests.get("https://meme-api.com/gimme")
    imgurl = response.json()['url']
    await interaction.response.send_message(imgurl)

@bot.tree.command(guild=guild)
async def berserk(interaction):
    """berk"""
    response = requests.get("https://meme-api.com/gimme/berserk")
    imgurl = response.json()['url']
    await interaction.response.send_message(imgurl)

@bot.tree.command(guild=guild)
async def waifu(interaction, type: str = "sfw", category: str = 'waifu'):
    """Throws a waifu"""
    if type == 'n':
        type = "nsfw"
    response = requests.get(f"https://api.waifu.pics/{type}/{category}")
    imgurl = response.json()['url']
    await interaction.response.send_message(imgurl)

@bot.tree.command(guild=guild)
async def traumatize(interaction):
    """truamatizes nearest viewer"""
    source = requests.get(f"https://e621.net/posts?page={random.randint(1,21)}&tags=hi_res+why", headers = headers)
    soup = BeautifulSoup(source.text, 'html.parser')
    Images = soup.find_all('img')
    img_links=[image['src'] for image in Images]
    await interaction.response.send_message(img_links[random.randint(2,65)])

@bot.tree.command(guild=guild)
async def fricks(interaction):
    """fucks stats"""
    message = ""
    with lock and open('data.json') as f:
        data = json.load(f)
    final = [user for user in data]
    final = sorted(final, key=lambda user: data[user]['fucks'], reverse=True)
    for user in final:
        message = message + f"{data[user]['name']}: {data[user]['fucks']}\n"
    await interaction.response.send_message(message)

@bot.tree.command(guild=guild)
async def quote(interaction):
    """says a quote"""
    with lock and open('quotes.json') as f:
        quotes = json.load(f)
    quote = random.choice(quotes)
    await interaction.response.send_message(f"\"{quote['quote']}\"\n\t- {quote['author']}")

@bot.command()
async def crote(ctx):
    """creates quote"""
    new_quote = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    with lock and open('quotes.json') as f:
        quotes = json.load(f)
    quotes.append({"quote": new_quote.content, "author": str(new_quote.author)})
    with lock and open('quotes.json', 'w') as f:
        json.dump(quotes, f, indent=2)
    await ctx.send(f"Ahh, dear adventurer! '{new_quote.content}'? A most radiant notion, spoken by a wise sage of another age! Truly, even in our darkest hours, the sun yet burns above! Never forget—there is glory in perseverance, and splendor in struggle. Praise the Sun! 🌞")

@bot.tree.command(guild=guild)
async def registerbday(interaction, birthday: str):
    """give yourself a bday mm-dd"""
    if len(birthday) != 5:
        pass
    with lock and open('data.json') as f:
        data = json.load(f)
    data[str(interaction.user.id)]['birthday'] = birthday
    with lock and open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message('Birthday registered')

@bot.tree.command(guild=guild)
async def resetdata(interaction):
    """resets data.json"""
    if interaction.user.id != ADMIN:
        await interaction.response.send_message("Admin only")
        return
    data = {}
    for user in interaction.guild.members:
        data[user.id] = {"name": user.name, "birthday": "mm-dd", "fucks": 0, "sunlight": 100, "battleid": 0}
    with lock and  open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message("data reset")

@bot.tree.command(guild=guild)
async def resetquotes(interaction):
    """resets quotes"""
    if interaction.user.id != ADMIN:
        await interaction.response.send_message("Admin only")
        return
    with lock and open('quotes.json', 'w') as f:
        json.dump(solaire_quotes, f, indent=2)
    await interaction.response.send_message("quotes reset")

@bot.tree.command(guild=guild)
async def balance(interaction):
    """Shows ya money"""
    with lock and open('data.json') as f:
        data = json.load(f)
    await interaction.response.send_message(f"Balance: {data[str(interaction.user.id)]['sunlight']} Sunlight", ephemeral=True)

#stock commands------------------------------------------------------------------------------

@bot.tree.command(guild=guild)
async def showstocks(interaction):
    """shows current stock prices"""
    message = ''
    with lock and open('stocks.json') as f:
        stocks = json.load(f)
    for stock in stocks:
        message = message + f"{stock}: {stocks[stock]['price']} Sunlight\n"
    await interaction.response.send_message(message, ephemeral=True)

@bot.tree.command(guild=guild)
async def portfolio(interaction):
    """shows your stocks"""
    userid = str(interaction.user.id)
    message = ''
    with lock and open('user-stocks.json') as f:
        investors = json.load(f)
    for stock in investors[userid]:
        message = message + f"{stock}: {investors[userid][stock]}\n"
    if message == '':
        await interaction.response.send_message("No stocks.... broke mf", ephemeral=True)
    await interaction.response.send_message(message, ephemeral=True)

async def stockname_autocomplete(interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    with lock and open('stocks.json') as f:
        stocks = json.load(f)
    choices = []
    for stock in stocks:
        if current.lower() in stock.lower():
            choices.append(app_commands.Choice(name=stock, value=stock))
    return choices

@bot.tree.command(guild=guild)
@app_commands.autocomplete(stockname=stockname_autocomplete)
async def buystock(interaction, stockname: str, amount: int = 1):
    """buys a stock"""
    if amount < 0:
        await interaction.response.send_message("NIGHTMARE NIGHTMARE NIGHTMARE NIGHTMARE NIGHTMARE", ephemeral=True)
        return
    userid = str(interaction.user.id)
    with lock and open('stocks.json') as f:
        stocks = json.load(f)
    if stockname not in stocks:
        await interaction.response.send_message("Invalid stock name", ephemeral=True)
        return
    total = stocks[stockname]['price'] * amount
    with lock and open('data.json') as f:
        data = json.load(f)
    if data[userid]['sunlight'] < total:
        await interaction.response.send_message(f"Not enought sunlight, total: {total} Sunlight, balance: {data[userid]['sunlight']} Sunlight, broke mf", ephemeral=True)
        return
    data[userid]['sunlight'] = round(data[userid]['sunlight'] - total, 2)
    with lock and open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    with lock and open('user-stocks.json') as f:
        investors = json.load(f)
    if stockname not in investors[userid]:
        investors[userid][stockname] = amount
    else:
        investors[userid][stockname] += amount
    with lock and open('user-stocks.json', 'w') as f:
        json.dump(investors, f, indent=2)
    await interaction.response.send_message(f"Bought {amount} shares of {stockname} for {total} Sunlight, Balance: {data[userid]['sunlight']} Sunlight", ephemeral=True)

@bot.tree.command(guild=guild)
@app_commands.autocomplete(stockname=stockname_autocomplete)
async def sellstock(interaction, stockname: str, amount: str = "1"):
    """sells a stock"""
    userid = str(interaction.user.id)
    with lock and open('user-stocks.json') as f:
        investors = json.load(f)
    if stockname not in investors[userid]:
        await interaction.response.send_message("You dont own any of this stock silly", ephemeral=True)
        return
    try:
        if investors[userid][stockname] <= int(amount):
            amount = investors[userid][stockname]
            del investors[userid][stockname]
        elif int(amount) < 0:
            await interaction.response.send_message("Don't go to sleep tonight", ephemeral=True)
            return
        else:
            investors[userid][stockname] -= int(amount)
    except:
        if amount != "all":
            await interaction.response.send_message("Invalid amount", ephemeral=True)
            return
        else:
            amount = investors[userid][stockname]
            del investors[userid][stockname]
    with lock and open('stocks.json') as f:
        stocks = json.load(f)
    total = stocks[stockname]['price'] * int(amount)
    with lock and open('user-stocks.json', 'w') as f:
        json.dump(investors, f, indent=2)
    with lock and open('data.json') as f:
        data = json.load(f)
    data[userid]['sunlight'] = round(data[userid]['sunlight'] + total, 2)
    with lock and open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message(f"Sold {amount} shares of {stockname} for {total} Sunlight, Balance: {data[userid]['sunlight']} Sunlight", ephemeral=True)

@bot.tree.command(guild=guild)
async def resetstocks(interaction):
    """resets the stock market"""
    if interaction.user.id != ADMIN:
        await interaction.response.send_message("Admin only")
        return
    with lock and open('stocks.json') as f:
        stocks = json.load(f)
    for key in stocks:
        stocks[key]['price'] = 3
        stocks[key]['favorlvl'] = 'neutral'
    with lock and open('stocks.json', 'w') as f:
        json.dump(stocks, f, indent=2)
    investors = {}
    for investor in interaction.guild.members:
        investors[investor.id] = {}
    with lock and open('user-stocks.json', 'w') as f:
        json.dump(investors, f, indent=2)
    await interaction.response.send_message("Stock market reset :(")

#item shop and inventory--------------------------------------------------------------------------

@bot.tree.command(guild=guild)
async def inventory(interaction):
    """shows your inventory"""
    userid = str(interaction.user.id)
    message = ''
    with lock and open('user-inventories.json') as f:
        inventories = json.load(f)
    for item in inventories[userid]:
        message = message + f"{item}: {inventories[userid][item]}\n"
    if message == '':
        await interaction.response.send_message("No items in inventory")
        return
    await interaction.response.send_message(message, ephemeral=True)

async def item_autocompletion(interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    with lock and open('user-inventories.json') as f:
        inventories = json.load(f)
    choices = []
    for item in inventories[str(interaction.user.id)]:
        if current.lower() in item.lower():
            choices.append(app_commands.Choice(name=item, value=item))
    return choices
            
@bot.tree.command(guild=guild)
@app_commands.autocomplete(item=item_autocompletion)
async def itemdesc(interaction, item: str):
    """shows an item's descritption"""
    userid = str(interaction.user.id)
    with lock and open('items.json') as f:
        items = json.load(f)
    if item not in items:
        await interaction.response.send_message("Invalid item")
    with lock and open('user-inventories.json') as f:
        inventories = json.load(f)
    if item not in inventories[userid]:
        await interaction.response.send_message("You do not own any of this item")
    embed = discord.Embed(title=item, description=items[item]['description'], color=rarity_colors[items[item]['rarity']])
    embed.add_field(name="Consumable", value=items[item]['consumable'], inline=True)
    embed.add_field(name="Equipable", value=items[item]['equipable'], inline=True)
    embed.add_field(name="Price", value=f"{items[item]['price']} Sunlight", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(guild=guild)
async def shop(interaction):
    """shows shop"""
    with lock and open('shop.json') as f:
        shop_items = json.load(f)
    embeds = []
    for item in shop_items:
        embed = discord.Embed(title=item, description=shop_items[item]['description'], color=rarity_colors[shop_items[item]['rarity']])
        embed.add_field(name="Consumable", value=shop_items[item]['consumable'], inline=True)
        embed.add_field(name="Equipable", value=shop_items[item]['equipable'], inline= True)
        embed.add_field(name="Price", value=f"{shop_items[item]['price']} Sunlight", inline=True)
        embeds.append(embed)
    await interaction.response.send_message(embeds=embeds, ephemeral=True)

async def shop_autocompletion(interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    with lock and open('shop.json') as f:
        shop_items = json.load(f)
    choices = []
    for item in shop_items:
        if current.lower() in item.lower():
            choices.append(app_commands.Choice(name=item, value=item))
    return choices

@bot.tree.command(guild=guild)
@app_commands.autocomplete(item=shop_autocompletion)
async def buyitem(interaction, item: str, amount: int = 1):
    """buys item"""
    if amount < 0:
        await interaction.response.send_message("You know what you did", ephemeral=True)
        return
    userid = str(interaction.user.id)
    with lock and open('shop.json') as f:
        shop_items = json.load(f)
    if item not in shop_items:
        await interaction.response.send_message("Item not in shop", ephemeral=True)
        return
    total = shop_items[item]['price'] * amount
    with lock and open('data.json') as f:
        data = json.load(f)
    if data[userid]['sunlight'] < total:
        await interaction.response.send_message(f"Not enought Sunlight, total: {total} Sunlight, balance: {data[userid]['sunlight']} Sunlight. broke mf", ephemeral=True)
        return
    data[userid]['sunlight'] = round(data[userid]['sunlight'] - total, 2)
    with lock and open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    with lock and open('user-inventories.json') as f:
        inventories = json.load(f)
    if item not in inventories[userid]:
        inventories[userid][item] = amount
    else:
        inventories[userid][item] += amount
    with lock and open('user-inventories.json', 'w') as f:
        json.dump(inventories, f, indent=2)
    await interaction.response.send_message(f"Bought {amount} {item} for {total}, balance {data[userid]['sunlight']} Sunlight", ephemeral=True)

@bot.tree.command(guild=guild)
@app_commands.autocomplete(item=item_autocompletion)
async def sellitem(interaction, item: str, amount: str = "1"):
    """sells item"""
    userid = str(interaction.user.id)
    with lock and open('user-inventories.json') as f:
        inventories = json.load(f)
    if item not in inventories[userid]:
        await interaction.response.send_message("Item not in inventory", ephemeral=True)
        return
    try:
        if inventories[userid][item] <= int(amount):
            amount = inventories[userid][item]
            del inventories[userid][item]
        elif int(amount) < 0:
            await interaction.response.send_message("I will eat your kidneys", ephemeral=True)
            return
        else:
            inventories[userid][item] -= int(amount)
    except:
        if amount != 'all':
            await interaction.response.send_message("Invalid amount", ephemeral=True)
            return
        else:
            amount = inventories[userid][item]
            del inventories[userid][item]
    with lock and open('user-inventories.json', 'w') as f:
        json.dump(inventories, f, indent=2)
    with lock and open('items.json') as f:
        items = json.load(f)
    total = items[item]['price'] * int(amount)
    with lock and open('data.json') as f:
        data = json.load(f)
    data[userid]['sunlight'] = round(data[userid]['sunlight'] + total, 2)
    with lock and open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message(f"Sold {amount} {item} for {total} Sunlight, balance {data[userid]['sunlight']} Sunlight", ephemeral=True)

@bot.tree.command(guild=guild)
async def resetshop(interaction):
    """resets the shop"""
    if interaction.user.id != ADMIN:
        await interaction.response.send_message("Admin only")
        return
    await shop_refresh()
    await interaction.response.send_message("Shop refreshed", ephemeral=True)

@bot.tree.command(guild=guild)
async def resetinventories(interaction):
    """resets inventories"""
    if interaction.user.id != ADMIN:
        await interaction.response.send_message("Admin only")
        return
    inventories = {}
    for user in interaction.guild.members:
        inventories[user.id] = {}
    with lock and open('user-inventories.json', 'w') as f:
        json.dump(inventories, f, indent=2)
    await interaction.response.send_message("Inventories reset")

@bot.tree.command(guild=guild)
async def testcolors(interaction):
    """tests colors"""
    channel = interaction.channel
    for key in rarity_colors:
        embed = discord.Embed(title=key, description=f"This color represents the {key} level of rarity", color=rarity_colors[key])
        await channel.send(embed=embed)
    await interaction.response.send_message("Rarity color embed test", ephemeral=True)
    
#gricklemon commands---------------------------------------------------------------------------------------------------------------------------------------------

def skill_to_embed(skillname: str, skill: dict) -> discord.Embed:
    scaling_string = "".join(f"{stat}: {scale}\n" for stat, scale in skill['scaling'].items())
    if len(skill['statuses']) == 0:
        status_string = "None"
    else: 
        status_string = "".join(f"{status}" for status in skill['statuses'])
    embed = discord.Embed(title=skillname, description=skill['description'], color=rarity_colors[skill['rarity']])
    embed.set_author(name=f"{skill['basedmg']} damage")
    embed.set_footer(text=f"Equiped: {skill['equiped']}")
    embed.add_field(name="Scaling:", value=scaling_string, inline=False)
    embed.add_field(name="Status Effects:", value=status_string, inline=False)
    return embed

def mon_to_embed(monname: str, mon: dict) -> discord.Embed:
    if len(mon['equiped'].keys()) == 0:
        equip_string = "None"
    else:
        equip_string = mon['equiped'].keys()[0]
    stats_string = "".join(f"{stat}: {value}\n" for stat, value in mon['stats'].items())
    skills_string = "".join(f"{skillname}: {skill['basedmg']}\n" for skillname, skill in mon['skills'].items())
    embed = discord.Embed(title=monname, description=mon['description'], color=rarity_colors[mon['rarity']])
    embed.set_author(name=f"lvl: {mon['lvl']} nextlvl: {mon['nextlvl']}")
    embed.set_footer(text=mon['type'])
    embed.add_field(name="Max Hp", value=mon['maxhp'], inline=True)
    embed.add_field(name="Current Hp", value=mon['currhp'], inline=True)
    embed.add_field(name="Stats:", value=stats_string, inline=False)
    embed.add_field(name="Skills:", value=skills_string, inline=False)
    embed.add_field(name="Equiped:", value=equip_string, inline=False)
    return embed

@bot.tree.command(guild=guild)
async def mons(interaction):
    """Shows your Gricklemon"""
    message = ""
    with lock and open('user-mons.json') as f:
        users_mons = json.load(f)
    user_mons = users_mons[str(interaction.user.id)]
    for mon in user_mons:
        message = message + f"{mon}: {user_mons[mon]['rarity']}\n"
    if message == "":
        await interaction.response.send_message("No Gricklemon in your possession", ephemeral=True)
        return
    await interaction.response.send_message(message, ephemeral=True)

@bot.tree.command(guild=guild)
async def skills(interaction):
    """Shows your skills"""
    message = ""
    with lock and open('user-skills.json') as f:
        users_skills = json.load(f)
    user_skills = users_skills[str(interaction.user.id)]
    for skill in user_skills:
        message = message + f"{skill}: {user_skills[skill]['rarity']}"
    if message == "":
        await interaction.response.send_message("No skills in your possession", ephemeral=True)
        return
    await interaction.response.send_message(message, ephemeral=True)

async def user_skill_autocompletion(interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    with lock and open('user-skills.json') as f:
        user_skills = json.load(f)
    choices = []
    for skill in user_skills[str(interaction.user.id)]:
        if current.lower() in skill.lower():
            choices.append(app_commands.Choice(name=skill, value=skill))
    return choices

@bot.tree.command(guild=guild)
@app_commands.autocomplete(skill=user_skill_autocompletion)
async def skilldesc(interaction, skill: str):
    """Shows skill description"""
    userid = str(interaction.user.id)
    with lock and open('user-skills.json') as f:
        users_skills = json.load(f)
    user_skills = users_skills[userid]
    if skill not in user_skills:
        await interaction.response.send_message("Skill not in your possession", ephemeral=True)
        return
    embed = skill_to_embed(skill, user_skills[skill])
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def user_mon_autocompletion(interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    with lock and open('user-mons.json') as f:
        user_mons = json.load(f)
    choices = []
    for mon in user_mons[str(interaction.user.id)]:
        if current.lower() in mon.lower():
            choices.append(app_commands.Choice(name=mon, value=mon))
    return choices

@bot.tree.command(guild=guild)
@app_commands.autocomplete(mon=user_mon_autocompletion)
async def mondesc(interaction, mon: str):
    """Shows Gricklemon description"""
    userid = str(interaction.user.id)
    with lock and open('user-mons.json') as f:
        users_mons = json.load(f)
    user_mons = users_mons[userid]
    if mon not in user_mons:
        await interaction.response.send_message("Gricklemon not in your possession", ephemeral=True)
        return
    embed = mon_to_embed(mon, user_mons[mon])
    await interaction.response.send_message(embed=embed, ephemeral=True)

def mon_to_usermon(skelemon: dict, lvl: int) -> dict:
    skelecopy = skelemon.copy()
    del skelecopy['banner']
    skelecopy['lvl'] = lvl
    grickle.lvl_up_stats(skelecopy, skelecopy)
    del skelecopy['statscales']
    skelecopy['maxhp'] = grickle.calc_hp(skelecopy, skelecopy)
    skelecopy['currhp'] = skelecopy['maxhp']
    del skelecopy['basehp']
    skelecopy['nextlvl'] = grickle.calc_next_level_exp(skelecopy)
    skelecopy['gaol'] = False
    skelecopy['away'] = False
    skelecopy['equiped'] = {}
    skelecopy['statuses'] = []
    return skelecopy

def skill_to_userskill(skeleskill: dict) -> dict:
    skelecopy = skeleskill.copy()
    del skelecopy['banner']
    skelecopy['equiped'] = False
    return skelecopy

@bot.tree.command(guild=guild)
async def pull(interaction):
    """Five pulls one Grickly boi"""
    userid = str(interaction.user.id)
    dupes = 0
    embeds = []
    with lock and open('user-inventories.json') as f:
        inventories = json.load(f)
    user_inventory = inventories[userid]
    if "Radiant Shard" not in user_inventory or user_inventory['Radiant Shard'] <= 5:
        await interaction.response.send_message("Not enought Radiant Shards", ephemeral=True)
        return
    if user_inventory['Radiant Shard'] == 5:
        del user_inventory['Radiant Shard']
    else:
        user_inventory['Radiant Shard'] -= 5
    inventories[userid] = user_inventory
    with lock and open('user-inventories.json', 'w') as f:
        json.dump(inventories, f, indent=2)
    with lock and open('gricklemon.json') as f:
        mons = json.load(f)
    with lock and open('banners.json') as f:
        banners = json.load(f)
    active_banner = banners['active']
    mon_list_rare = {mon: value for mon, value in mons.items() if value['banner'] == active_banner and value['rarity'] == 'Rare'}
    mon_list_legendary = {mon: value for mon, value in mons.items() if value['banner'] == active_banner and value['rarity'] == 'Legendary'}
    rarity = random.choices(["Rare", "Legendary"], weights=[95,5])[0]
    match rarity:
        case "Rare":
            chosen_boi = random.choice(list(mon_list_rare.keys()))
        case "Legendary":
            chosen_boi = random.choice(list(mon_list_legendary.keys()))
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    if chosen_boi in boxes[userid]:
        dupes += 1
    else:
        boxes[userid][chosen_boi] = mon_to_usermon(mons[chosen_boi], lvl=1)
        with lock and open('user-mons.json', 'w') as f:
            json.dump(boxes, f, indent=2)
    embeds.append(mon_to_embed(chosen_boi, boxes[userid][chosen_boi]))
    with lock and open('skills.json') as f:
        skills = json.load(f)
    with lock and open('user-skills.json') as f:
        skill_boxes = json.load(f)
    skill_list_common = {skill: value for skill, value in skills.items() if value['banner'] == active_banner and value['rarity'] == "Common"}
    skill_list_uncommon = {skill: value for skill, value in skills.items() if value['banner'] == active_banner and value['rarity'] == "Uncommon"}
    skill_list_rare = {skill: value for skill, value in skills.items() if value['banner'] == active_banner and value['rarity'] == "Rare"}
    skill_list_legendary = {skill: value for skill, value in skills.items() if value['banner'] == active_banner and value['rarity'] == "Legendary"}
    skill_list_incandescent = {skill: value for skill, value in skills.items() if value['banner'] == active_banner and value['rarity'] == "Incandescent"}
    already_chosen = []
    for _ in range(5):
        while True:
            rarity = random.choices(["Common", "Uncommon", "Rare", "Legendary", "Incandescent"], weights=[45, 25, 15, 10, 5])[0]
            match rarity:
                case "Common":
                    chosen_skill = random.choice(list(skill_list_common.keys()))
                    if chosen_skill not in already_chosen:
                        already_chosen.append(chosen_skill)
                        break
                case "Uncommon":
                    chosen_skill = random.choice(list(skill_list_uncommon.keys()))
                    if chosen_skill not in already_chosen:
                        already_chosen.append(chosen_skill)
                        break
                case "Rare":
                    chosen_skill = random.choice(list(skill_list_rare.keys()))
                    if chosen_skill not in already_chosen:
                        already_chosen.append(chosen_skill)
                        break
                case "Legendary":
                    chosen_skill = random.choice(list(skill_list_legendary.keys()))
                    if chosen_skill not in already_chosen:
                        already_chosen.append(chosen_skill)
                        break
                case "Incandescent":
                    chosen_skill = random.choice(list(skill_list_incandescent.keys()))
                    if chosen_skill not in already_chosen:
                        already_chosen.append(chosen_skill)
                        break
        if chosen_skill in skill_boxes[userid]:
            dupes += 1
        else:
            skill_boxes[userid][chosen_skill] = skill_to_userskill(skills[chosen_skill])
        embeds.append(skill_to_embed(chosen_skill, skill_boxes[userid][chosen_skill]))
    with lock and open('user-skills.json', 'w') as f:
        json.dump(skill_boxes, f, indent=2)
    with lock and open('items.json') as f:
        items = json.load(f)
    dupe_return = dupes * (items['Radiant Shard']['price'] / 2)
    with lock and open('data.json') as f:
        data = json.load(f)
    data[userid]['sunlight'] += dupe_return
    with lock and open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message(f"dupes: {dupes}, Sunlight back: {dupe_return}", embeds=embeds, ephemeral=True)

async def mon_not_away_autocomplete(interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    box = boxes[str(interaction.user.id)]
    choices = []
    for mon in box:
        if current.lower() in mon.lower() and not box[mon]['away'] and not box[mon]['gaol']:
            choices.append(app_commands.Choice(name=mon, value=mon))
    return choices

async def skill_not_equiped_autocomplete(interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    with lock and open('user-skills.json') as f:
        skillboxes = json.load(f)
    skillbox = skillboxes[str(interaction.user.id)]
    choices = []
    for skill in skillbox:
        if current.lower() in skill.lower() and not skillbox[skill]['equiped']:
            choices.append(app_commands.Choice(name=skill, value=skill))
    return choices

@bot.tree.command(guild=guild)
@app_commands.autocomplete(mon=mon_not_away_autocomplete)
@app_commands.autocomplete(skill=skill_not_equiped_autocomplete)
async def equipskill(interaction, mon: str, skill: str):
    """Equips a skill to a Grickle"""
    userid = str(interaction.user.id)
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    with lock and open('user-skills.json') as f:
        skillboxes = json.load(f)
    box = boxes[userid]
    skillbox = skillboxes[userid]
    if mon not in box or box[mon]['away'] or box[mon]['gaol']:
        await interaction.response.send_message(f"Invalid Gricklemon", ephemeral=True)
        return
    if skill not in skillbox or skillbox[skill]['equiped']:
        await interaction.response.send_message(f"Invalid Skill", ephemeral=True)
        return
    if len(box[mon]['skills']) == 4:
        await interaction.response.send_message(f"Can only equip 4 skills", ephemeral=True)
        return
    box[mon]['skills'][skill] = skillbox[skill]
    skillbox[skill]['equiped'] = True
    boxes[userid] = box
    skillboxes[userid] = skillbox
    with lock and open('user-mons.json', 'w') as f:
        json.dump(boxes, f, indent=2)
    with lock and open('user-skills.json', 'w') as f:
        json.dump(skillboxes, f, indent=2)
    await interaction.response.send_message(f"Equiped {skill} to {mon}", ephemeral=True)

async def equiped_skill_autocomplete(interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    with lock and open('user-skills.json') as f:
        skillboxes = json.load(f)
    skillbox = skillboxes[str(interaction.user.id)]
    choices = []
    for skill in skillbox:
        if current.lower() in skill.lower() and skillbox[skill]['equiped']:
            choices.append(app_commands.Choice(name=skill, value=skill))
    return choices

@bot.tree.command(guild=guild)
@app_commands.autocomplete(mon=mon_not_away_autocomplete)
@app_commands.autocomplete(skill=equiped_skill_autocomplete)
async def unequipskill(interaction, mon: str, skill: str):
    """Unequips a skill from a Grickly boi"""
    userid = str(interaction.user.id)
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    with lock and open('user-skills.json') as f:
        skillboxes = json.load(f)
    box = boxes[userid]
    skillbox = skillboxes[userid]
    if mon not in box or box[mon]['away'] or box[mon]['gaol']:
        await interaction.response.send_message("Invalid Gricklemon", ephemeral=True)
        return
    if skill not in box[mon]['skills']:
        await interaction.response.send_message("Invalid Skill", ephemeral=True)
        return
    if len(box[mon]['skills']) == 1:
        await interaction.response.send_message("Gricklemon can not have no skills", ephemeral=True)
        return
    skillbox[skill]['equiped'] = False
    del box[mon]['skills'][skill]
    boxes[userid] = box
    skillboxes[userid] = skillbox
    with lock and open('user-mons.json', 'w') as f:
        json.dump(boxes, f, indent=2)
    with lock and open('user-skills.json', 'w') as f:
        json.dump(skillboxes, f, indent=2)
    await interaction.response.send_message(f"Unequiped {skill} from {mon}", ephemeral=True)

class MonSelect(discord.ui.Select):
    def __init__(self, user: discord.User, box: list):
        self.user = user
        options = [discord.SelectOption(label=mon, value=mon) for mon in box]
        super().__init__(placeholder="Choose a Gricklemon", min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("Stay out of this bub", ephemeral=True)
            return
        self.view.selected_value = self.values[0]
        await interaction.response.defer()

class ConfirmChallengeButton(discord.ui.Button):
    def __init__(self, user: discord.User):
        super().__init__(label="Accept", style=discord.ButtonStyle.green)
        self.user = user
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("Jolly cooperation not allowed", ephemeral=True)
            return
        if not self.view.selected_value:
            await interaction.response.send_message("Please select a Gricklemon before accepting.")
            return
        await interaction.response.defer()
        self.view.confirmed = True
        self.view.stop()

class ChallengeView(discord.ui.View):
    def __init__(self, user: discord.User, box: list):
        super().__init__(timeout=120)
        self.selected_value = None
        self.confirmed = False
        self.add_item(MonSelect(user, box))
        self.add_item(ConfirmChallengeButton(user))

@bot.tree.command(guild=guild)
@app_commands.autocomplete(mon=mon_not_away_autocomplete)
async def challenge(interaction, vs: discord.User, mon: str):
    """Challenges a user"""
    userid = str(interaction.user.id)
    enemyid = str(vs.id)
    with lock and open('data.json') as f:
        data = json.load(f)
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    box = boxes[userid]
    if enemyid == "1209602748908048464":
        await interaction.response.send_message("You wish to challenge me? Maybe if you were more incandescent I'd take you seriously.", ephemeral=True)
        return
    if enemyid == userid:
        await interaction.response.send_message("Invalid user", ephemeral=True)
        return
    if data[enemyid]['battleid'] != 0:
        await interaction.response.send_message("User already in battle", ephemeral=True)
        return
    if mon not in box or box[mon]['away'] or box[mon]['gaol']:
        await interaction.response.send_message("Invalid Gricklemon", ephemeral=True)
        return
    enemybox = boxes[enemyid]
    view = ChallengeView(vs, list(enemybox.keys()))
    await interaction.response.send_message(f"{vs.mention}, {interaction.user.mention} has challenged you to a Gricklemon duel. Select a mon and confirm or hide in the shadows.", view=view)
    await view.wait()
    if view.confirmed:
        with lock and open('battles.json') as f:
            battles = json.load(f)
        battles[battles['nextid']] = {userid: {mon: box[mon]}, enemyid: {view.selected_value: enemybox[view.selected_value]}, "turn": enemyid}
        box[mon]['away'] = True
        enemybox[view.selected_value]['away'] = True
        data[userid]['battleid'] = battles['nextid']
        data[enemyid]['battleid'] = battles['nextid']
        battles['nextid'] += 1
        boxes[userid] = box
        boxes[enemyid] = enemybox
        with lock and open('battles.json', 'w') as f:
            json.dump(battles, f, indent=2)
        with lock and open('data.json', 'w') as f:
            json.dump(data, f, indent=2)
        with lock and open('user-mons.json', 'w') as f:
            json.dump(boxes, f, indent=2)
        await interaction.followup.send(f"{vs.mention} has accepted the challenge, {vs.mention} has the first turn")
    else:
        await interaction.followup.send(f"{vs.mention} did not accept the challenge or failed to notice in time.")
    try:
        message = await interaction.original_response()
        await message.delete()
    except discord.NotFound():
        pass

@bot.tree.command(guild=guild)
@app_commands.autocomplete(mon=mon_not_away_autocomplete)
async def battle(interaction, mon: str):
    """Starts a battle with a random mon from active banner"""
    userid = str(interaction.user.id)
    with lock and open('data.json') as f:
        data = json.load(f)
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    box = boxes[userid]
    if data[userid]['battleid'] != 0:
        await interaction.response.send_message("You're already in a battle genius.", ephemeral=True)
        return
    if mon not in box or box[mon]['away'] or box[mon]['gaol']:
        await interaction.response.send_message("Invalid Gricklemon", ephemeral=True)
        return
    with lock and open('banners.json') as f:
        banners = json.load(f)
    active_banner = banners['active']
    with lock and open('gricklemon.json') as f:
        mons = json.load(f)
    banner_mons_rare = {mon: value for mon, value in mons.items() if value['rarity'] == "Rare" and value['banner'] == active_banner}
    banner_mons_legendary = {mon: value for mon, value in mons.items() if value['rarity'] == "Legendary" and value['banner'] == active_banner}
    rarity = random.choices(["Rare", "Legendary"], weights=[65, 35])[0]
    match rarity:
        case "Rare":
            chosen_boi = random.choice(list(banner_mons_rare.keys()))
        case "Legendary":
            chosen_boi = random.choice(list(banner_mons_legendary.keys()))
    with lock and open('battles.json') as f:
        battles = json.load(f)
    enemylvl = random.randint(max(box[mon]['lvl'] - 10, 0), box[mon]['lvl'] + 10)
    battles[battles['nextid']] = {userid: {mon: box[mon]}, "ai": {chosen_boi: mon_to_usermon(mons[chosen_boi], lvl=enemylvl)}, "turn": userid}
    box[mon]['away'] = True
    data[userid]['battleid'] = battles['nextid']
    battles['nextid'] += 1
    boxes[userid] = box
    with lock and open('battles.json', 'w') as f:
        json.dump(battles, f, indent=2)
    with lock and open('user-mons.json', 'w') as f:
        json.dump(boxes, f, indent=2)
    with lock and open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message(f"Battle started with lvl {enemylvl} {rarity} {chosen_boi}. The battle starts with your turn.", ephemeral=True)

async def end_battle(interaction: discord.Interaction, winner: str, loser: str, battles: dict, data: dict):
    userid = str(interaction.user.id)
    battleid = str(data[userid]['battleid'])
    battle = battles[battleid]
    loserid = [key for key in list(battle.keys()) if key != userid and key != 'turn'][0]
    winnermon = battle[userid][winner]
    startlvl = winnermon['lvl']
    losermon = battle[loserid][loser]
    exp = grickle.drop_exp(winnermon, losermon)
    losermon['gaol'] = True
    with lock and open('gricklemon.json') as f:
        mons = json.load(f)
    grickle.process_lvls(winnermon, mons[winner], exp)
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    winnermon['away'] = False
    boxes[userid][winner] = winnermon
    if loserid != 'ai':
        boxes[loserid][loser] = losermon
    with lock and open('user-mons.json', 'w') as f:
        json.dump(boxes, f, indent=2)
    message = f"{winner} defeated {loser} and gained {exp} exp."
    if startlvl != winnermon['lvl']:
        message = message + f"\n{winner} leveled up {startlvl} -> {winnermon['lvl']}"
    with lock and open('banners.json') as f:
        banners = json.load(f)
    active_banner = banners[banners['active']]
    ephemeral = False
    if loserid == 'ai':
        ephemeral = True
        sunlight = round(grickle.drop_sunlight(losermon), 2)
        data[userid]['sunlight'] = round(data[userid]['sunlight'] + sunlight, 2)
        message = message + f"\nGained {sunlight} Sunlight"
        drop_pool = list(active_banner['drop-pool'].keys())
        drop = random.choice(drop_pool)
        if drop == 'none':
            pass
        else:
            with lock and open('user-inventories.json') as f:
                inventories = json.load(f)
            inventory = inventories[userid]
            if drop not in inventory:
                inventory[drop] = active_banner['drop-pool'][drop]
            else:
                inventory[drop] += 1
            inventories[userid] = inventory
            with lock and open('user-inventories.json', 'w') as f:
                json.dump(inventories, f, indent=2)
            message = message + f"\n{loser} dropped {drop}"
    del battles[battleid]
    with lock and open('battles.json', 'w') as f:
        json.dump(battles, f, indent=2)
    data[userid]['battleid'] = 0
    with lock and open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message(message, ephemeral=ephemeral)

async def battle_skill_autocomplete(interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    with lock and open('battles.json') as f:
        battles = json.load(f)
    with lock and open('data.json') as f:
        data = json.load(f)
    userid = str(interaction.user.id)
    battleid = str(data[userid]['battleid'])
    monname = list(battles[battleid][userid].keys())[0]
    mon = battles[battleid][userid][monname]
    choices = []
    for skill in mon['skills']:
        if current.lower() in skill.lower():
            choices.append(app_commands.Choice(name=skill, value=skill))
    return choices

@bot.tree.command(guild=guild)
@app_commands.autocomplete(skill=battle_skill_autocomplete)
async def attack(interaction, skill: str):
    """Attacks with a skill"""
    userid = str(interaction.user.id)
    with lock and open('data.json') as f:
        data = json.load(f)
    battleid = str(data[userid]['battleid'])
    if battleid == 0:
        await interaction.response.send_message("Erm you're not in a battle dumbass", ephemeral=True)
        return
    with lock and open('battles.json') as f:
        battles = json.load(f)
    battle = battles[battleid]
    if battle['turn'] != userid:
        await interaction.response.send_message("WAIT YOUR TURN!!!!!!", ephemeral=True)
        return
    mon = list(battle[userid].keys())[0]
    #start_of_turn_checks() do this tomorrow (today) -----------------------------------------------------------------------------------
    if skill not in battle[userid][mon]['skills']:
        await interaction.response.send_message("Invalid skill", ephemeral=True)
        return
    enemyid = [enemyid for enemyid in battle if enemyid != userid and enemyid != 'turn'][0]
    if enemyid == 'ai':
        ephemeral = True
    else:
        ephemeral = False
    enemymon = list(battle[enemyid].keys())[0]
    if round(random.random(), 2) <= grickle.hit_chance(battle[userid][mon], battle[enemyid][enemymon]):
        damage = round(grickle.damage(battle[userid][mon], battle[enemyid][enemymon], battle[userid][mon]['skills'][skill]), 2)
        battle[enemyid][enemymon]['currhp'] -= damage
    else:
        await interaction.response.send_message("Attack missed", ephemeral=ephemeral)
        battle['turn'] = enemyid
        battles[battleid] = battle
        with lock and open('battles.json', 'w') as f:
            json.dump(battles, f, indent=2)
        return
    if battle[enemyid][enemymon]['currhp'] <= 0:
        await end_battle(interaction, mon, enemymon, battles, data)
        return
    status_msg = ''
    for status in battle[userid][mon]['skills'][skill]['statuses']:
        if round(random.random(), 2) <= grickle.status_proc_chance(battle[userid], battle[enemyid]):
            status_msg = status_msg + f"{status} "
            battle[enemyid][enemymon]['statuses'].append(status)
    if len(battle[enemyid][enemymon]['statuses']) == 0:
        message = f"Used {skill} for {damage} damage {enemymon} hp remaining: {battle[enemyid][enemymon]['currhp']}"
    else:
        message = f"Used {skill} for {damage} and applied statuses: {status_msg} {enemymon} hp remaining: {battle[enemyid][enemymon]['currhp']}"
    battle['turn'] = enemyid
    battles[battleid] = battle
    with lock and open('battles.json', 'w') as f:
        json.dump(battles, f, indent=2)
    await interaction.response.send_message(message, ephemeral=ephemeral)

#running utility-----------------------------------------------------------------------------------------------

def main():
    bot.run(TOKEN)

if __name__ == "__main__":
    main()