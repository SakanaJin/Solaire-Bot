import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import shutil
import random
import requests
from bs4 import BeautifulSoup
import json
import datetime
import asyncio
import typing
import math

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

headsortails = ["heads", "tails"]
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
solaire_quotes = [{"quote": "Praise the sun!", "author": "Solaire"}, {"quote": "If only I could be so grossly incandescent", "author": "Solaire"}, {"quote": "Oh, hello there. I will stay behind, to gaze at the sun. The sun is a wondrous body. Like a magnificent father", "author": "Solaire"}, {"quote": "You really are fond of chatting with me, aren't you? If I didn't know better, I'd think you had feelings for me! Ha ha ha", "author": "Solaire"}, {"quote": "I am Solaire of Astora, an adherent of the Lord of Sunlight. Now that I am Undead, I have come to this great land, the birthplace of Lord Gwyn, to seek my very own sun", "author": "Solaire"}, {"quote": "We are amidst strange beings, in a strange land. The flow of time itself is convoluted; with heroes centuries old phasing in and out", "author": "Solaire"}]
critical_files = ['stocks.json', 'skills.json', 'items.json', 'gricklemon.json', 'boss-mons.json', 'banners.json']
gen_files = ['user-monuments.json', 'dungeon.json', 'user-stocks.json', 'user-skills.json', 'user-mons.json', 'user-inventories.json', 'shop.json', 'quotes.json', 'gaol.json', 'data.json', 'battles.json']
stock_favorlvls = ['hated', 'poor', 'none', 'favored', 'loved']
rarity_colors = {"Common": 0xf7faf8, "Uncommon": 0x14c744, "Rare": 0x1791e8, "Legendary": 0x7217e8, "Incandescent": 0xfcb632, "Key-Item": 0x068067, "Monument": 0xfcf914}
bot_tasks = {}
lock = asyncio.Lock()

#file generation-------------------------------------------------------------------------------------

file_gen_handlers = {}

async def create_backup() -> bool:
    directory = os.listdir()
    try:
        if not os.path.exists("backup"):
            os.mkdir("backup")
        for file in directory:
            if file.endswith(".json") and file not in critical_files:
                shutil.copy2(file, "backup")
        return True
    except:
        return False

def register_file_generator(file_name):
    def decorator(func):
        file_gen_handlers[file_name] = func
        return func
    return decorator

async def id_dict_files(file: str, members) -> None:
    dict_of_ids = {}
    for user in members:
        dict_of_ids[str(user.id)] = {}
    with lock and open(file, 'w') as f:
        json.dump(dict_of_ids, f, indent=2)

@register_file_generator(file_name="data.json")
async def handle_gen_data(file: str, members, **kwargs) -> None:
    data = {}
    for user in members:
        data[str(user.id)] = {"name": user.name, "birthday": "mm-dd", "fucks": 0, "sunlight": 100, "battleid": 0}
    with lock and open(file, 'w') as f:
        json.dump(data, f, indent=2)

@register_file_generator(file_name="battles.json")
async def handle_gen_battles(file: str, **kwargs) -> None:
    battles = {"nextid": 1}
    with lock and open(file, 'w') as f:
        json.dump(battles, f, indent=2)

@register_file_generator(file_name="gaol.json")
async def handle_gen_gaol(file: str, members, **kwargs) -> None:
    gaols = {}
    for user in members:
        gaols[str(user.id)] = []
    with lock and open(file, 'w') as f:
        json.dump(gaols, f, indent=2)

@register_file_generator(file_name="quotes.json")
async def handle_gen_quotes(file: str, **kwargs) -> None:
    with lock and open(file, 'w') as f:
        json.dump(solaire_quotes, f, indent=2)

@register_file_generator(file_name="shop.json")
async def handle_gen_shop(file: str, **kwargs) -> None:
    await shop_refresh()

@register_file_generator(file_name="user-inventories.json")
async def handle_gen_userinventories(file: str, members, **kwargs) -> None:
    await id_dict_files(file=file, members=members)

@register_file_generator(file_name="user-mons.json")
async def handle_gen_usermons(file: str, members, **kwargs) -> None:
    await id_dict_files(file=file, members=members)

@register_file_generator(file_name="user-skills.json")
async def handle_gen_userskills(file: str, members, **kwargs) -> None:
    await id_dict_files(file=file, members=members)

@register_file_generator(file_name="user-stocks.json")
async def handle_gen_userstocks(file: str, members, **kwargs) -> None:
    await id_dict_files(file=file, members=members)

@register_file_generator(file_name="dungeon.json")
async def handle_gen_dungeon(file: str, members, **kwargs) -> None:
    await id_dict_files(file=file, members=members)

@register_file_generator(file_name="user-monuments.json")
async def handle_gen_monuments(file: str, members, **kwargs) -> None:
    await id_dict_files(file=file, members=members)

#events-----------------------------------------------------------------------------------------------

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord")
    global general
    general = await bot.fetch_channel(CID)
    admin = await bot.fetch_user(ADMIN)
    print("Checking critical files\n")
    files = os.listdir()
    for file in critical_files:
        if file not in files:
            print(f"{file} not found in directory, creating backup and attempting to download from github\n")
            backedup = await create_backup(files)
            if backedup:
                print("backup created")
            else:
                print("failed to create backup terminating session")
                await bot.close()
                return
            try:
                response = requests.get(f"https://raw.githubusercontent.com/SakanaJin/Solaire-Bot/refs/heads/main/{file}") # this will only work if the repository is public
                response.raise_for_status()
                with lock and open(file, 'wb') as f:
                    f.write(response.content)
                print(f"{file} created")
            except requests.HTTPError as e:
                print(f"{e} failed to get {file} from github terminating session")
                await bot.close()
                return
        else: print(f"{file} found in directory")
    print("Critical file check complete\n")
    print("Chekcing user data files\n")
    touched = False
    for file in gen_files:
        if file not in files and not touched:
            print(f"{file} not found in directory, data reset reccomended")
            await admin.send(f"{file} not found in directory use '/generatedatafiles' to create a back up and generate all the data files")
            touched = True
        else:
            print(f"{file} found in directory")
    print("User data file check complete\n")
    print("Starting tasks")        
    stock_check.start()
    bot_tasks['Stock Report'] = stock_check
    birthday_check.start()
    bot_tasks['Birthday Checks'] = birthday_check
    shop_refresh.start()
    bot_tasks['Shop Refresh'] = shop_refresh
    gaol_refresh.start()
    bot_tasks['Gaol Break'] = gaol_refresh
    health_reset.start()
    bot_tasks['Health Reset'] = health_reset
    dungeon_updates.start()
    bot_tasks['Dungeon Update'] = dungeon_updates
    banner_check.start()
    print("Started tasks")

@bot.event
async def on_member_join(member):
    with lock and open('data.json') as f:
        data = json.load(f)
    data[member.id] = {"name": member.name, "birthday": "mm-dd", "fucks": 0, "sunlight": 100, "battleid": 0}
    with lock and open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await general.send(f"Welcome to the server {member.name}! Enjoying the sunlight?")

#tasks--------------------------------------------------------------------------------------------------

@tasks.loop(time=datetime.time(hour=15, minute=0)) #1000 cdt -> 1500 utc
async def birthday_check():
    with lock and open('data.json') as f:
        data = json.load(f)
    for userid in data:
        if data[userid]['birthday'] == str(datetime.date.today().strftime("%m-%d")):
            await general.send(f"Ahh, @everyone... Today is no ordinary day—it is a day of radiance! A day to honor you, a most noble and unwavering soul. Happy birthday, brave {data[userid]['name']}! With each passing year, your light grows stronger, shining boldly even through the deepest dark. May your journey ahead be filled with jolly cooperation, hearty laughter, and the warmth of the ever-glorious sun! So come—raise your arms high, and let us rejoice! Praise it! Praise the Sun! ☀️")

@tasks.loop(time=datetime.time(hour=17, minute=0)) #1200 cdt -> 1700 utc
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
                percent_change = random.uniform(-0.20, 0.02)
            case 'poor':
                percent_change = random.uniform(-0.05, 0.02)
            case 'none':
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
        await asyncio.sleep(1)
    with open('stocks.json', 'w') as f: # might need a lock
        json.dump(stocks, f, indent=2)
    await general.send(message)

@tasks.loop(time=datetime.time(hour=17, minute=30)) #1230 cdt -> 1730 utc
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

@tasks.loop(time=datetime.time(hour=11, minute=0)) #0600 cdt -> 1100 utc
async def gaol_refresh():
    with lock and open('gaol.json') as f:
        gaols = json.load(f)
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    for userid, monlist in gaols.items():
        for mon in monlist:
            boxes[userid][mon]['gaol'] = False
            boxes[userid][mon]['away'] = False
            boxes[userid][mon]['currhp'] = boxes[userid][mon]['maxhp']
            boxes[userid][mon]['statuses'] = []
        gaols[userid] = []
    with lock and open('goal.json', 'w') as f:
        json.dump(gaols, f, indent=2)
    with lock and open('user-mons.json', 'w') as f:
        json.dump(boxes, f, indent=2)

@tasks.loop(time=datetime.time(hour=10, minute=0)) #0500 cdt -> 1000 utc
async def health_reset():
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    for userid, monlist in boxes.items():
        for mon in monlist:
            if not boxes[userid][mon]['away'] or boxes[userid][mon]['gaol']:
                boxes[userid][mon]['currhp'] = boxes[userid][mon]['maxhp']
    with lock and open('user-mons.json', 'w') as f:
        json.dump(boxes, f, indent=2)

@tasks.loop(hours=1)
async def dungeon_updates():
    with lock and open('data.json') as f:
        data = json.load(f)
    with lock and open('dungeon.json') as f:
        dungeons = json.load(f)
    userids = [key for key in data if dungeons[key] != []]
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    with lock and open('gricklemon.json') as f:
        mons = json.load(f)
    for userid in userids:
        user = await bot.fetch_user(int(userid))
        for mon in dungeons[userid]:
            how_solaire_feelin_bout_dis = random.choices(stock_favorlvls, weights=[5,25,40,25,5])[0]
            match how_solaire_feelin_bout_dis:
                case "hated":
                    damage = random.randint(math.floor(boxes[userid][mon]['maxhp'] * 0.3), math.floor(boxes[userid][mon]['maxhp']))
                    exp = 0
                case "poor":
                    damage = random.randint(math.floor(boxes[userid][mon]['maxhp'] * 0.05), math.floor(boxes[userid][mon]['maxhp'] * 0.30))
                    exp = random.randint(math.floor(boxes[userid][mon]['nextlvl'] * 0.05), math.floor(boxes[userid][mon]['nextlvl'] * 0.10))
                case "none":
                    damage = random.randint(math.floor(boxes[userid][mon]['maxhp'] * 0.05), math.floor(boxes[userid][mon]['maxhp'] * 0.1))
                    exp = random.randint(math.floor(boxes[userid][mon]['nextlvl'] * 0.05), math.floor(boxes[userid][mon]['nextlvl'] * 0.20))
                case "favored":
                    damage = random.randint(math.floor(boxes[userid][mon]['maxhp'] * 0.01), math.floor(boxes[userid][mon]['maxhp'] * 0.05))
                    exp = random.randint(math.floor(boxes[userid][mon]['nextlvl'] * 0.05), math.floor(boxes[userid][mon]['nextlvl'] * 0.3))
                case "loved":
                    damage = 0
                    exp = random.randint(math.floor(boxes[userid][mon]['nextlvl'] * 0.1), math.floor(boxes[userid][mon]['nextlvl'] * 0.3))
            dungeons[userid][mon]['currhp'] -= damage
            if dungeons[userid][mon]['currhp'] <= 0:
                boxes[userid][mon] = dungeons[userid][mon]
                boxes[userid][mon]['gaol'] = True
                boxes[userid][mon]['away'] = False
                del dungeons[userid][mon]
                await user.send(f"{mon} in the dungeon has fucking died and been sent to Gaol lmao")
            else:
                grickle.process_lvls(dungeons[userid][mon], mons[mon], exp)
                boxes[userid][mon] = dungeons[userid][mon]
                await user.send(f"{mon} in the dungeon has gained {exp} exp and lost {damage} health")
    with lock and open('dungeon.json', 'w') as f:
        json.dump(dungeons, f, indent=2)
    with lock and open('user-mons.json', 'w') as f:
        json.dump(boxes, f, indent=2)

@tasks.loop(time=datetime.time(hour=11, minute=30)) #0630 cdt -> 1130 utc
async def banner_check():
    with lock and open('banners.json') as f:
        banners = json.load(f)
    print(datetime.date.today())
    if datetime.date.today().strftime("%Y-%m-%d") != banners['change-date']:
        return
    banners['change-date'] = (datetime.date.today() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
    bannerchoices = [banner for banner in banners if banner != "change-date" and banner != "active"] #later on add filtering for repeat banners after you create multiple
    chosen_banner = random.choice(bannerchoices)
    banners['active'] = chosen_banner
    with lock and open('banners.json', 'w') as f:
        json.dump(banners, f, indent=2)
    await general.send(f"@everyone a new banner has been selected", embed=banner_to_embed(chosen_banner, banners[chosen_banner]))

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
async def createbackup(interaction):
    """Creates a backup of all data files"""
    if interaction.user.id != ADMIN:
        await interaction.response.send_message("Admin only", ephemeral=True)
        return
    backedup = await create_backup()
    if not backedup:
        await interaction.response.send_message("Failed to create backup", ephemeral=True)
        return
    await interaction.response.send_message("Backup created", ephemeral=True)

@bot.tree.command(guild=guild)
async def generatedatafiles(interaction):
    """Creates a backup then generates / regenerates data files"""
    if interaction.user.id != ADMIN:
        await interaction.response.send_message("Admin only", ephemeral=True)
        return
    backedup = await create_backup()
    if not backedup:
        await interaction.response.send_message("Failed to create backup terminating process", ephemeral=True)
        return
    for file in gen_files:
        await file_gen_handlers[file](file=file, members=interaction.guild.members)
    await interaction.response.send_message("Data reset you can find any of the old data in the ./backups directory", ephemeral=True)

@bot.tree.command(guild=guild)
async def schedule(interaction):
    """Shows scheduled tasks"""
    message = f"timezone: utc (subtract 5 hours for cdt)\n"
    for taskname, task in bot_tasks.items():
        next_run = task.next_iteration
        message += f"{taskname}: {next_run.strftime('%m-%d, %H:%M')}\n"
    await interaction.response.send_message(message, ephemeral=True)

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

def banner_to_embed(bannername: str, banner: dict) -> discord.Embed:
    with lock and open('boss-mons.json') as f:
        bosses = json.load(f)
    with lock and open('banners.json') as f:
        banners = json.load(f)
    bannerbosses = [boss for boss in bosses if bosses[boss]['banner'] == bannername]
    embed = discord.Embed(title=bannername, description=banner['description'], color=rarity_colors[banner['rarity']])
    embed.set_author(name=f"Active until: {banners['change-date']}")
    for boss in bannerbosses:
        embed.add_field(name=boss, value=f"{bosses[boss]['description']}\nneeded: {bosses[boss]['key']}\nlvl: {bosses[boss]['lvl']}\ntype: {bosses[boss]['type']}")
    return embed

def monument_to_embed(monumentname: str, monument: dict) -> discord.Embed:
    embed = discord.Embed(title=monumentname, description=monument['description'], color=rarity_colors[monument['rarity']])
    embed.set_author(name=f"Banner: {monument['banner']}")
    return embed

def boss_to_embed(bossname: str, boss: dict) -> discord.Embed:
    embed = discord.Embed(title=bossname, description=boss['description'], color=rarity_colors['Incandescent'])
    embed.set_author(name=f"lvl: {boss['lvl']}")
    embed.set_footer(text=f"Type: {boss['type']}")
    embed.add_field(name="Needed:", value=boss['key'])
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
    rarity = random.choices(["Rare", "Legendary"], weights=[80,20])[0]
    match rarity:
        case "Rare":
            chosen_boi = random.choice(list(mon_list_rare.keys()))
        case "Legendary":
            chosen_boi = random.choice(list(mon_list_legendary.keys()))
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    with lock and open('skills.json') as f:
        skills = json.load(f)
    with lock and open('user-skills.json') as f:
        skill_boxes = json.load(f)
    if chosen_boi in boxes[userid]:
        dupes += 1
    else:
        boxes[userid][chosen_boi] = mon_to_usermon(mons[chosen_boi], lvl=5)
        for skill in boxes[userid][chosen_boi]['skills']:
            skill_boxes[userid][skill] = boxes[userid][chosen_boi]['skills'][skill]
        with lock and open('user-mons.json', 'w') as f:
            json.dump(boxes, f, indent=2)
    embeds.append(mon_to_embed(chosen_boi, boxes[userid][chosen_boi]))
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
    enemymonkeysfiltered = [key for key in enemybox.keys() if not enemybox[key]['away'] and not enemybox[key]['gaol']]
    view = ChallengeView(vs, enemymonkeysfiltered)
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
    enemylvl = random.randint(max(box[mon]['lvl'] - banners[active_banner]['lvlweights'][0], 1), box[mon]['lvl'] + banners[active_banner]['lvlweights'][1])
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

async def end_battle(interaction: discord.Interaction, winnerid: str, winner: str, loser: str, battles: dict, data: dict):
    userid = str(interaction.user.id)
    battleid = str(data[userid]['battleid'])
    battle = battles[battleid]
    loserid = [key for key in list(battle.keys()) if key != winnerid and key != 'turn'][0]
    winnermon = battle[winnerid][winner]
    startlvl = winnermon['lvl']
    losermon = battle[loserid][loser]
    exp = grickle.drop_exp(winnermon, losermon)
    if loserid != 'ai':
        losermon['gaol'] = True
        with lock and open('gaol.json') as f:
            gaols = json.load(f)
        gaols[loserid].append(loser)
        with lock and open('gaol.json', 'w') as f:
            json.dump(gaols, f, indent=2)
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    if winnerid == "ai":
        await interaction.followup.send(f"{winner} has defeated you and {loser} has been sent to Gaol", ephemeral=True)
        boxes[loserid][loser] = losermon
        boxes[loserid][loser]['away'] = False
        del battles[battleid]
        data[loserid]['battleid'] = 0
        with lock and open('user-mons.json', 'w') as f:
            json.dump(boxes, f, indent=2)
        with lock and open('battles.json', 'w') as f:
            json.dump(battles, f, indent=2)
        with lock and open('data.json', 'w') as f:
            json.dump(data, f, indent=2)
        return
    with lock and open('gricklemon.json') as f:
        mons = json.load(f)
    grickle.process_lvls(winnermon, mons[winner], exp)
    winnermon['away'] = False
    losermon['away'] = False
    winnermon['statuses'] = []
    losermon['statuses'] = []
    boxes[winnerid][winner] = winnermon
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
        data[winnerid]['sunlight'] = round(data[winnerid]['sunlight'] + sunlight, 2)
        message = message + f"\nGained {sunlight} Sunlight"
        drop_pool = list(active_banner['drop-pool'].keys())
        drop = random.choice(drop_pool)
        if drop == 'none':
            pass
        else:
            with lock and open('user-inventories.json') as f:
                inventories = json.load(f)
            inventory = inventories[winnerid]
            if drop not in inventory:
                inventory[drop] = 1
            else:
                inventory[drop] += 1
            inventories[winnerid] = inventory
            with lock and open('user-inventories.json', 'w') as f:
                json.dump(inventories, f, indent=2)
            message = message + f"\n{loser} dropped {drop}"
        if losermon.get('monument') != None:
            with lock and open('user-monuments.json') as f:
                user_monuments = json.load(f)
            monumentname = list(losermon['monument'].keys())[0]
            user_monuments[userid][monumentname] = losermon['monument'][monumentname]
            with lock and open('user-monuments.json', 'w') as f:
                json.dump(user_monuments, f, indent=2)
    del battles[battleid]
    with lock and open('battles.json', 'w') as f:
        json.dump(battles, f, indent=2)
    data[winnerid]['battleid'] = 0
    with lock and open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    embed = mon_to_embed(winner, battle[winnerid][winner])
    await interaction.followup.send(message, embed=embed, ephemeral=ephemeral)

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
    message = ""
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
    if skill not in battle[userid][mon]['skills']:
        await interaction.response.send_message("Invalid skill", ephemeral=True)
        return
    enemyid = [enemyid for enemyid in battle if enemyid != userid and enemyid != 'turn'][0]
    if enemyid == 'ai':
        ephemeral = True
    else:
        ephemeral = False
    enemymon = list(battle[enemyid].keys())[0]
    for status in battle[userid][mon]['statuses']:
        message = message + grickle.status_hadler[status](battle[userid][mon], battle[enemyid][enemymon])
    if battle[userid][mon]['currhp'] <= 0:
        await interaction.response.send_message(message, ephemeral=ephemeral)
        await end_battle(interaction, enemyid, enemymon, mon, battles, data)
        return
    if "is paralyzed" in message:
        battle['turn'] = enemyid
        battles[battleid] = battle
        with lock and open('battles.json', 'w') as f:
            json.dump(battles, f, indent=2)
        await interaction.response.send_message(message, ephemeral=ephemeral)
        if enemyid == "ai":
            await ai_turn(interaction, enemymon, mon)
        return
    if round(random.random(), 2) <= grickle.hit_chance(battle[userid][mon], battle[enemyid][enemymon]):
        damage = round(grickle.damage(battle[userid][mon], battle[enemyid][enemymon], battle[userid][mon]['skills'][skill]), 2)
        battle[enemyid][enemymon]['currhp'] = math.floor(battle[enemyid][enemymon]['currhp'] - damage)
    else:
        battle['turn'] = enemyid
        battles[battleid] = battle
        with lock and open('battles.json', 'w') as f:
            json.dump(battles, f, indent=2)
        await interaction.response.send_message("Attack missed", ephemeral=ephemeral)
        if enemyid == "ai":
            await ai_turn(interaction, enemymon, mon)
        return
    status_msg = ''
    for status in battle[userid][mon]['skills'][skill]['statuses']:
        if round(random.random(), 2) <= grickle.status_proc_chance(battle[userid][mon], battle[enemyid][enemymon]) and status not in battle[enemyid][enemymon]['statuses']:
            status_msg = status_msg + f"{status} "
            battle[enemyid][enemymon]['statuses'].append(status)
    if status_msg == '':
        message = message + f"Used {skill} for {damage} damage {enemymon} hp remaining: {battle[enemyid][enemymon]['currhp']}"
    else:
        message = message + f"Used {skill} for {damage} and applied statuses: {status_msg} {enemymon} hp remaining: {battle[enemyid][enemymon]['currhp']}"
    if battle[enemyid][enemymon]['currhp'] <= 0:
        await interaction.response.send_message(message, ephemeral=ephemeral)
        await end_battle(interaction, userid, mon, enemymon, battles, data)
        return
    battle['turn'] = enemyid
    battles[battleid] = battle
    with lock and open('battles.json', 'w') as f:
        json.dump(battles, f, indent=2)
    await interaction.response.send_message(message, ephemeral=ephemeral)
    if enemyid == "ai":
        await ai_turn(interaction, enemymon, mon)

async def useable_item_autocomplete(interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    with lock and open('user-inventories.json') as f:
        inventories = json.load(f)
    with lock and open('items.json') as f:
        items = json.load(f)
    inventory = inventories[str(interaction.user.id)]
    choices = []
    for item in inventory:
        if current.lower() in item.lower() and items[item]['consumable']:
            choices.append(app_commands.Choice(name=item, value=item))
    return choices

@bot.tree.command(guild=guild)
@app_commands.autocomplete(item=useable_item_autocomplete)
async def useitem(interaction, item: str):
    """Uses an item"""
    userid = str(interaction.user.id)
    message = ""
    with lock and open('data.json') as f:
        data = json.load(f)
    with lock and open('user-inventories.json') as f:
        inventories = json.load(f)
    with lock and open('items.json') as f:
        items = json.load(f)
    inventory = inventories[userid]
    if item not in inventory or not items[item]['consumable']:
        await interaction.response.send_message("Invalid item", ephemeral=True)
        return
    battleid = str(data[userid]['battleid'])
    if battleid == "0" or items[item]['nobattleonly']:
        with lock and open('user-mons.json') as f:
            boxes = json.load(f)
        monkeysfiltered = [key for key in boxes[userid] if not boxes[userid][key]['away'] or not boxes[userid][key]['gaol']]
        view = ChallengeView(interaction.user, monkeysfiltered)
        await interaction.response.send_message("Pick a Gricklemon to use item on", view=view, ephemeral=True)
        await view.wait()
        if view.confirmed:
            message = grickle.item_handler[item](boxes[userid][view.selected_value])
            if '\0' in message:
                await interaction.followup.send(message, ephemeral=True)
                return
            inventory[item] -= 1
            if inventory[item] == 0:
                del inventory[item]
            inventories[userid] = inventory
            with lock and open('user-inventories.json', 'w') as f:
                json.dump(inventories, f, indent=2)
            with lock and open('user-mons.json', 'w') as f:
                json.dump(boxes, f, indent=2)
            await interaction.followup.send(message, embed=mon_to_embed(view.selected_value, boxes[userid][view.selected_value]), ephemeral=True)
        else:
            await interaction.followup.send("Failed to select in time", ephemeral=True)
        try:
            msg = await interaction.original_response()
            await msg.delete()
        except discord.NotFound():
            pass
        return
    with lock and open('battles.json') as f:
        battles = json.load(f)
    battle = battles[battleid]
    mon = list(battle[userid].keys())[0]
    enemyid = [key for key in battle if key != userid and key != 'turn'][0]
    enemymon = list(battle[enemyid].keys())[0]
    ephemeral = False
    if enemyid == 'ai':
        ephemeral = True
    for status in battle[userid][mon]['statuses']:
        message = message + grickle.status_hadler[status](battle[userid][mon], battle[enemyid][enemymon])
    if battle[userid][mon]['currhp'] <= 0:
        await interaction.response.send_message(message, ephemeral=ephemeral)
        await end_battle(interaction, enemyid, enemymon, mon, battles, data)
        return
    if "is paralyzed" in message:
        battle['turn'] = enemyid
        battles[battleid] = battle
        with lock and open('battles.json', 'w') as f:
            json.dump(battles, f, indent=2)
        await interaction.response.send_message(message, ephemeral=ephemeral)
        if enemyid == "ai":
            await ai_turn(interaction, enemymon, mon)
        return
    message = grickle.item_handler[item](battle[userid][mon])
    inventory[item] -= 1
    if inventory[item] == 0:
        del inventory[item]
    inventories[userid] = inventory
    with lock and open('user-inventories.json', 'w') as f:
        json.dump(inventories, f, indent=2)
    battle['turn'] = enemyid
    battles[battleid] = battle
    with lock and open('battles.json', 'w') as f:
        json.dump(battles, f, indent=2)
    await interaction.response.send_message(message, ephemeral=ephemeral)
    if enemyid == "ai":
        await ai_turn(interaction, enemymon, mon)

@bot.tree.command(guild=guild)
async def run(interaction):
    """Try to flee battle"""
    message = ''
    userid = str(interaction.user.id)
    with lock and open('data.json') as f:
        data = json.load(f)
    battleid = str(data[userid]['battleid'])
    if battleid == '0':
        await interaction.response.send_message("Cant run from a battle you're not in.", ephemeral=True)
        return
    with lock and open('battles.json') as f:
        battles = json.load(f)
    battle = battles[battleid]
    if battle['turn'] != userid:
        await interaction.response.send_message("Wait your turn to flee coward", ephemeral=True)
    mon = list(battle[userid].keys())[0]
    enemyid = [key for key in battle if key != userid and key != 'turn'][0]
    enemymon = list(battle[enemyid].keys())[0]
    ephemeral = False
    if enemyid == 'ai':
        ephemeral = True
    for status in battle[userid][mon]['statuses']:
        message = message + grickle.status_hadler[status](battle[userid][mon], battle[enemyid][enemymon])
    if battle[userid][mon]['currhp'] <= 0:
        await interaction.response.send_message(message, ephemeral=ephemeral)
        await end_battle(interaction, enemyid, enemymon, mon, battles, data)
        return
    if "is paralyzed" in message:
        battle['turn'] = enemyid
        battles[battleid] = battle
        with lock and open('battles.json', 'w') as f:
            json.dump(battles, f, indent=2)
        await interaction.response.send_message(message, ephemeral=ephemeral)
        if enemyid == "ai":
            await ai_turn(interaction, enemymon, mon)
        return
    if random.random() >= grickle.flee_chance(battle[userid][mon], battle[enemyid][enemymon]):
        with lock and open('user-mons.json') as f:
            boxes = json.load(f)
        boxes[userid][mon]['away'] = False
        del battles[battleid]
        data[userid]['battleid'] = 0
        if enemyid != 'ai':
            data[userid]['battleid'] = 0
        with lock and open('battles.json', 'w') as f:
            json.dump(battles, f, indent=2)
        with lock and open('data.json', 'w') as f:
            json.dump(data, f, indent=2)
        with lock and open('user-mons.json', 'w') as f:
            json.dump(boxes, f, indent=2)
        await interaction.response.send_message("Fled from battle", ephemeral=ephemeral)
        return
    battle['turn'] = enemyid
    battles[battleid] = battle
    with lock and open('battles.json', 'w') as f:
        json.dump(battles, f, indent=2)
    await interaction.response.send_message("Failed to flee", ephemeral=ephemeral)
    if enemyid == "ai":
        await ai_turn(interaction, enemymon, mon)

async def ai_turn(interaction: discord.Interaction, aimon: str, enemymon: str):
    enemyid = str(interaction.user.id)
    userid = 'ai'
    message = ''
    with lock and open('data.json') as f:
        data = json.load(f)
    with lock and open('battles.json') as f:
        battles = json.load(f)
    battleid = str(data[enemyid]['battleid'])
    battle = battles[battleid]
    for status in battle[userid][aimon]['statuses']:
        message = message + grickle.status_handler[status](battle[userid][aimon], battle[enemyid][enemymon])
    if battle[userid][aimon]['currhp'] <= 0:
        await interaction.followup.send(message, ephemeral=True)
        await end_battle(interaction, userid, enemymon, aimon, battles, data)
        return
    if "is paralyzed" in message:
        battle['turn'] = enemyid
        battles[battleid] = battle
        with lock and open('battles.json', 'w') as f:
            json.dump(battles, f, indent=2)
        await interaction.followup.send(message, ephemeral=True)
        return
    skills = list(battle['ai'][aimon]['skills'].keys())
    skill = random.choice(skills)
    if round(random.random(), 2) <= grickle.hit_chance(battle[userid][aimon], battle[enemyid][enemymon]):
        damage = round(grickle.damage(battle[userid][aimon], battle[enemyid][enemymon], battle[userid][aimon]['skills'][skill]), 2)
        battle[enemyid][enemymon]['currhp'] = math.floor(battle[enemyid][enemymon]['currhp'] - damage)
    else:
        await interaction.followup.send("Attack missed", ephemeral=True)
        battle['turn'] = enemyid
        battles[battleid] = battle
        with lock and open('battles.json', 'w') as f:
            json.dump(battles, f, indent=2)
        return
    status_msg = ''
    for status in battle[userid][aimon]['skills'][skill]['statuses']:
        if round(random.random(), 2) <= grickle.status_proc_chance(battle[userid][aimon], battle[enemyid][enemymon]) and status not in battle[enemyid][enemymon]['statuses']:
            status_msg = status_msg + f"{status} "
            battle[enemyid][enemymon]['statuses'].append(status)
    if status_msg == '':
        message = message + f"Used {skill} for {damage} damage {enemymon} hp remaining: {battle[enemyid][enemymon]['currhp']}"
    else:
        message = message + f"Used {skill} for {damage} and applied statuses: {status_msg} {enemymon} hp remaining: {battle[enemyid][enemymon]['currhp']}"
    if battle[enemyid][enemymon]['currhp'] <= 0:
        await interaction.followup.send(message, ephemeral=True)
        await end_battle(interaction, "ai", aimon, enemymon, battles, data)
        return
    battle['turn'] = enemyid
    battles[battleid] = battle
    with lock and open('battles.json', 'w') as f:
        json.dump(battles, f, indent=2)
        await interaction.followup.send(message, ephemeral=True)

@bot.tree.command(guild=guild)
async def battleinfo(interaction):
    """Shows current battle information"""
    userid = str(interaction.user.id)
    with lock and open('data.json') as f:
        data = json.load(f)
    with lock and open('battles.json') as f:
        battles = json.load(f)
    battleid = str(data[userid]['battleid'])
    if battleid == "0":
        await interaction.response.send_message("No battle to get info from bozo", ephemeral=True)
        return
    battle = battles[battleid]
    embeds = [mon_to_embed(list(battle[user].keys())[0], battle[user][list(battle[user].keys())[0]]) for user in battle if user != "turn"]
    if battle['turn'] == 'ai':
        user = 'ai'
    else:
        user = await interaction.guild.fetch_member(battle['turn'])
    await interaction.response.send_message(f"turn: {user}", embeds=embeds, ephemeral=True)

@bot.tree.command(guild=guild)
async def gaol(interaction):
    """Shows the Gaol"""
    userid = str(interaction.user.id)
    message = ""
    with lock and open('gaol.json') as f:
        gaols = json.load(f)
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    for mon in gaols[userid]:
        if not boxes[userid][mon]['gaol']:
            gaols[userid].remove(mon)
        message = message + f"{mon}\n"
    with lock and open('gaol.json', 'w') as f:
        json.dump(gaols, f, indent=2)
    if len(gaols[userid]) == 0 or message == "":
        await interaction.response.send_message("Gaol Empty", ephemeral=True)
        return
    await interaction.response.send_message(message, ephemeral=True)

@bot.tree.command(guild=guild)
@app_commands.autocomplete(mon=mon_not_away_autocomplete)
async def sendtodungeon(interaction, mon: str):
    """Sends mon to the dungeon"""
    userid = str(interaction.user.id)
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    if mon not in boxes[userid] or boxes[userid][mon]['away'] or boxes[userid][mon]['gaol']:
        await interaction.response.send_message("Invalid Gricklemon", ephemeral=True)
        return
    with lock and open('dungeon.json') as f:
        dungeons = json.load(f)
    if len(dungeons[userid]) == 3:
        await interaction.response.send_message("Cant have more than 3 Gricklemons in the dungeon at a time", ephemeral=True)
    dungeons[userid][mon] = boxes[userid][mon]
    boxes[userid][mon]['away'] = True
    with lock and open('user-mons.json', 'w') as f:
        json.dump(boxes, f, indent=2)
    with lock and open('dungeon.json', 'w') as f:
        json.dump(dungeons, f, indent=2)
    await interaction.response.send_message(f"{mon} sent to the dungeon", ephemeral=True)

async def mon_in_dungeon(interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    userid = str(interaction.user.id)
    with lock and open('dungeon.json') as f:
        dungeons = json.load(f)
    choices = []
    for mon in dungeons[userid]:
        if current.lower() in mon.lower():
            choices.append(app_commands.Choice(name=mon, value=mon))
    return choices

@bot.tree.command(guild=guild)
@app_commands.autocomplete(mon=mon_in_dungeon)
async def returnfromdungeon(interaction, mon: str):
    """Returns mon from dungeon"""
    userid = str(interaction.user.id)
    with lock and open('dungeon.json') as f:
        dungeons = json.load(f)
    if mon not in dungeons[userid]:
        await interaction.response.send_message("Invalid Gricklemon", ephemeral=True)
        return
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    boxes[userid][mon] = dungeons[userid][mon]
    boxes[userid][mon]['away'] = False
    del dungeons[userid][mon]
    with lock and open('user-mons.json', 'w') as f:
        json.dump(boxes, f, indent=2)
    with lock and open('dungeon.json', 'w') as f:
        json.dump(dungeons, f, indent=2)
    await interaction.response.send_message(f"{mon} returned from the dungeon", ephemeral=True)
 
@bot.tree.command(guild=guild)
async def dungeoninfo(interaction):
    """Shows Gricklemon in the dungeon"""
    userid = str(interaction.user.id)
    with lock and open('dungeon.json') as f:
        dungeons = json.load(f)
    if len(dungeons[userid]) == 0:
        await interaction.response.send_message("No mons in dungeon", ephemeral=True)
        return
    embeds = []
    for mon in dungeons[userid]:
        embeds.append(mon_to_embed(mon, dungeons[userid][mon]))
    await interaction.response.send_message("Mons in the dungeon", embeds=embeds, ephemeral=True)

@bot.tree.command(guild=guild)
async def banner(interaction, name: str = "active"):
    with lock and open('banners.json') as f:
        banners = json.load(f)
    if name not in banners or name != "active":
        await interaction.response.send_message("Invalid banner name", ephemeral=True)
        return
    if name == "active":
        name = banners['active']
    await interaction.response.send_message(embed=banner_to_embed(name, banners[name]), ephemeral=True)

async def bannerboss_autocomplete(interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    with lock and open('banners.json') as f:
        banners = json.load(f)
    with lock and open('boss-mons.json') as f:
        bosses = json.load(f)
    choices = []
    for boss in bosses:
        if current.lower() in boss.lower() and bosses[boss]['banner'] == banners['active']:
            choices.append(app_commands.Choice(name=boss, value=boss))
    return choices

@bot.tree.command(guild=guild)
@app_commands.autocomplete(boss=bannerboss_autocomplete)
@app_commands.autocomplete(mon=mon_not_away_autocomplete)
async def boss(interaction, boss: str, mon: str):
    """Challenge a banner boss"""
    userid = str(interaction.user.id)
    with lock and open('boss-mons.json') as f:
        bosses = json.load(f)
    with lock and open('banners.json') as f:
        banners = json.load(f)
    with lock and open('user-inventories.json') as f:
        inventories = json.load(f)
    with lock and open('user-mons.json') as f:
        boxes = json.load(f)
    with lock and open('battles.json') as f:
        battles = json.load(f)
    with lock and open('data.json') as f:
        data = json.load(f)
    active_banner = banners["active"]
    if boss not in bosses or bosses[boss]['banner'] != active_banner:
        await interaction.response.send_message("Invalid Boss", ephemeral=True)
        return
    if bosses[boss]['key'] not in inventories[userid]:
        await interaction.response.send_message("You don't have the right boy", ephemeral=True)
        return
    if mon not in boxes[userid] or boxes[userid][mon]['away'] or boxes[userid][mon]['gaol']:
        await interaction.response.send_message("Invalid Gricklemon", ephemeral=True)
        return
    inventories[userid][bosses[boss]['key']] -= 1
    if inventories[userid][bosses[boss]['key']] == 0:
        del inventories[userid][bosses[boss]['key']]
    battleid = battles['nextid']
    battles['nextid'] += 1
    battles[battleid] = {userid: {mon: boxes[userid][mon]}, "ai": {boss: bosses[boss]}, "turn": userid}
    boxes[userid][mon]['away'] = True
    data[userid]['battleid'] = battleid
    with lock and open('battles.json', 'w') as f:
        json.dump(battles, f, indent=2)
    with lock and open('user-inventories.json', 'w') as f:
        json.dump(inventories, f, indent=2)
    with lock and open('user-mons.json', 'w') as f:
        json.dump(boxes, f, indent=2)
    with lock and open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message(bosses[boss]['entrancemsg'], ephemeral=True)

@bot.tree.command(guild=guild)
async def monuments(interaction):
    """Displays your Monuments"""
    userid = str(interaction.user.id)
    with lock and open('user-monuments.json') as f:
        user_monuments = json.load(f)
    if len(user_monuments[userid]) == 0:
        await interaction.response.send_message("You dont have any Monuments yet. Bet your maidenless too.", ephemeral=True)
        return
    embeds = []
    for monumentname in user_monuments[userid]:
        embeds.append(monument_to_embed(monumentname, user_monuments[userid][monumentname]))
    await interaction.response.send_message("Monuments of your strength", embeds=embeds, ephemeral=True)

@bot.tree.command(guild=guild)
@app_commands.autocomplete(boss=bannerboss_autocomplete)
async def bossdesc(interaction, boss: str):
    """Shows the description of a boss in the active banner"""
    with lock and open('boss-mons.json') as f:
        bosses = json.load(f)
    with lock and open('banners.json') as f:
        banners = json.load(f)
    if boss not in bosses or bosses[boss]['banner'] != banners['active']:
        await interaction.response.send_message("Invalid Boss", ephemeral=True)
        return
    await interaction.response.send_message(embed=boss_to_embed(boss, bosses[boss]), ephemeral=True)

#running utility-----------------------------------------------------------------------------------------------

def main():
    bot.run(TOKEN)

if __name__ == "__main__":
    main()