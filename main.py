import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import random
import requests
from bs4 import BeautifulSoup
import json
import datetime
import asyncio
import typing

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
    data[member.id] = {"name": member.name, "birthday": "mm-dd", "fucks": 0, "sunlight": 100}
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
            stocks[stock]['favorlvl'] = random.choices(stock_favorlvls, weights=[5,25,50,25,5])[0]
    for stock in stocks:
        match stocks[stock]['favorlvl']:
            case 'hated':
                percent_change = random.uniform(-0.20, 0.02)
            case 'poor':
                percent_change = random.uniform(-0.05, 0.02)
            case 'neutral':
                percent_change = random.uniform(-0.02, 0.05)
            case 'favored':
                percent_change = random.uniform(-0.02, 0.15)
            case 'loved':
                percent_change = random.uniform(-0.02, 0.20)
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
        data[user.id] = {"name": user.name, "birthday": "mm-dd", "fucks": 0, "sunlight": 100}
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
    

def main():
    bot.run(TOKEN)

if __name__ == "__main__":
    main()