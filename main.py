import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import random
import requests
from bs4 import BeautifulSoup
import json
import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CID = os.getenv('CID')
GID = os.getenv('GID')
ADMIN = os.getenv('ADMIN')

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

#events-----------------------------------------------------------------------------------------------

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord")
    global general
    general = await bot.fetch_channel(CID)
    birthday_check.start()
    stock_check.start()

@bot.event
async def on_member_join(member):
    with open('data.json') as f:
        data = json.load(f)
    data.append({"id": member.id, "name": str(member.name), "birthday": "mm-dd", "fucks": 0})
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await general.send(f"Welcome to the server {member.name}! Enjoying the sunlight?")

#tasks--------------------------------------------------------------------------------------------------

@tasks.loop(time=datetime.time(hour=15, minute=0)) #1500 utc 1000 cdt
async def birthday_check():
    with open('data.json') as f:
        data = json.load(f)
    for user in data:
        if user['birthday'] == str(datetime.date.today().strftime("%m-%d")):
            await general.send(f"Ahh, @everyone... Today is no ordinary day—it is a day of radiance! A day to honor you, a most noble and unwavering soul. Happy birthday, brave {user['name']}! With each passing year, your light grows stronger, shining boldly even through the deepest dark. May your journey ahead be filled with jolly cooperation, hearty laughter, and the warmth of the ever-glorious sun! So come—raise your arms high, and let us rejoice! Praise it! Praise the Sun! ☀️")

@tasks.loop(time=datetime.time(hour=17, minute=0)) #1700 utc 1200 cdt
async def stock_check():
    message = f"Sunlight stock market report - {datetime.date.today()}\n"
    with open('sotcks.json') as f:
        stocks = json.load(f)
    if datetime.date.today().weekday() == 0 or 4: # monday and thursday
        for stock in stocks:
            stock['favorlvl'] = random.choice(stock_favorlvls, weights=[5,25,50,25,5])
    for stock in stocks:
        match stock['favorlvl']:
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
        stock['price'] += round(stock['price'] * percent_change, 2)
        sign = ""
        if percent_change > 0:
            sign = "+"
        message = message + f"{stock['name']}: {stock['price']} sunlight ({sign}{percent_change * 100}%)\n"
    await general.send(message)

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
    with open('data.json') as f:
        data = json.load(f)
    for user in data:
        if user['name'] == str(author):
            user['fucks'] += 1
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)

#commands--------------------------------------------------------------------------------------------------

@bot.tree.command(guild=guild)
async def test(interaction):
    """:3"""
    await interaction.response.send_message(":3")

@bot.command()
async def sync(ctx):
    """syncs commands"""
    if ctx.author.name != ADMIN:
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
    with open('data.json') as f:
        data = json.load(f)
    data = sorted(data, key=lambda user: user['fucks'], reverse=True)
    for user in data:
        message = message + f"{user['name']}: {user['fucks']}\n"
    await interaction.response.send_message(message)

@bot.tree.command(guild=guild)
async def quote(interaction):
    """says a quote"""
    with open('quotes.json') as f:
        quotes = json.load(f)
    quote = random.choice(quotes)
    await interaction.response.send_message(f"\"{quote['quote']}\"\n\t- {quote['author']}")

@bot.command()
async def crote(ctx):
    """creates quote"""
    new_quote = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    with open('quotes.json') as f:
        quotes = json.load(f)
    quotes.append({"quote": new_quote.content, "author": str(new_quote.author)})
    with open('quotes.json', 'w') as f:
        json.dump(quotes, f, indent=2)
    await ctx.send(f"Ahh, dear adventurer! '{new_quote.content}'? A most radiant notion, spoken by a wise sage of another age! Truly, even in our darkest hours, the sun yet burns above! Never forget—there is glory in perseverance, and splendor in struggle. Praise the Sun! 🌞")

@bot.tree.command(guild=guild)
async def registerbday(interaction, birthday: str):
    """give yourself a bday mm-dd"""
    if len(birthday) != 5:
        pass
    with open('data.json') as f:
        data = json.load(f)
    for user in data:
        if user['name'] == interaction.user.name:
            user['birthday'] = birthday
            break
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message('Birthday registered')

@bot.tree.command(guild=guild)
async def resetdata(interaction):
    """resets data.json"""
    if interaction.user.name != ADMIN:
        await interaction.response.send_message("Admin only")
        return
    data = [{"id": user.id, "name": user.name, "birthday": "mm-dd", "fucks": 0} for user in interaction.guild.members]
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message("data reset")

@bot.tree.command(guild=guild)
async def resetquotes(interaction):
    """resets quotes"""
    if interaction.user.name != ADMIN:
        await interaction.response.send_message("Admin only")
        return
    with open('quotes.json', 'w') as f:
        json.dump(solaire_quotes, f, indent=2)
    await interaction.response.send_message("quotes reset")

@bot.tree.command(guild=guild)
async def balance(interaction):
    """Shows ya money"""
    with open('data.json') as f:
        data = json.load(f)
    for user in data:
        if user['id'] == interaction.user.id:
            await interaction.response.send_message(f"Balance: {user['sunlight']} Sunlight")
            break

#stock commands------------------------------------------------------------------------------

@bot.tree.command(guild=guild)
async def showstocks(interaction):
    """shows current stock prices"""
    message = ''
    with open('stocks.json') as f:
        stocks = json.load(f)
    for stock in stocks:
        message = message + f"{stock['name']}: {stock['price']} Sunlight\n"
    await interaction.response.send_message(message)

@bot.tree.command(guild=guild)
async def portfolio(interaction):
    """shows your stocks"""
    message = ''
    with open('user-stocks.json') as f:
        investors = json.load(f)
    for investor in investors:
        if investor['name'] == interaction.user.name:
            for stock in investor['stocks']:
                message = message + f"{stock['name']}: {stock['amount']}\n"
            break
    if message == '':
        await interaction.response.send_message("No stocks.... broke mf")
    await interaction.response.send_message(message)

@bot.tree.command(guild=guild)
async def buystock(interaction, stockname: str, amount: int = 1):
    """buys a stock"""
    price = 0
    with open('stocks.json') as f:
        stocks = json.load(f)
    for stock in stocks:
        if stock['name'].lower() == stockname.lower():
            price = stock['price']
            break
    if price == 0:
        await interaction.response.send_message("Invalid stock name")
        return
    total = price * amount
    with open('data.json') as f:
        data = json.load(f)
    for user in data:
        if interaction.user.name == user['name']:
            if user['sunlight'] < total:
                await interaction.response.send_message(f"Too expensive.\nPrice: {total}\nYour Sunlight:{user['Sunlight']}")
                return
            user['sunlight'] = user['sunlight'] - total
            remainder = user['sunlight']
            break
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    with open('user-stocks.json') as f:
        investors = json.load(f)
    found = False
    for investor in investors:
        if investor['name'] == interaction.user.name:
            for investor_stock in investor['stocks']:
                if investor_stock['name'].lower() == stockname.lower():
                    investor_stock['amount'] = investor_stock['amount'] + amount
                    found = True
                    break
            if not found:
                investor['stocks'].append({"name": stockname, "amount": amount})
            break
    with open('user-stocks.json', 'w') as f:
        json.dump(investors, f, indent=2)
    await interaction.response.send_message(f"Bought {amount} share of {stockname} for {total}, remaining Sunlight: {remainder}")

@bot.tree.command(guild=guild)
async def sellstock(interaction, stockname: str, amount: str = "1"):
    """sells a stock"""
    price = 0
    with open('stocks.json') as f:
        stocks = json.load(f)
    for stock in stocks:
        if stock['name'].lower() == stockname.lower():
            price = stock['price']
            break
    if price == 0:
        await interaction.response.send_message("Invalid stock name")
        return
    with open('user-stocks.json') as f:
        investors = json.load(f)
    found = False
    for investor in investors:
        if investor['name'] == interaction.user.name:
            for investor_stock in investor['stocks']:
                if investor_stock['name'].lower() == stockname.lower():
                    toremove = investor_stock
                    found = True
                    try:
                        if investor_stock['amount'] < int(amount):
                            amount = investor_stock['amount']
                            investor_stock['amount'] = 0
                            break
                        investor_stock['amount'] = investor_stock['amount'] - int(amount)
                        break
                    except ValueError:
                        if amount.lower() == "all":
                            amount = investor_stock['amount']
                            investor_stock['amount'] = 0
                            break
                        await interaction.response.send_message(f"{amount} is not a valid amount.")
                        return
            if toremove['amount'] == 0:
                investor['stocks'].remove(toremove)
            break
    if not found:
        await interaction.response.send_message("You don't own any of that stock silly")
        return
    with open('user-stocks.json', 'w') as f:
        json.dump(investors, f, indent=2)
    total = price * int(amount)
    with open('data.json') as f:
        data = json.load(f)
    for user in data:
        if user['name'] == interaction.user.name:
            user['sunlight'] = user['sunlight'] + total
            balance = user['sunlight']
            break
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message(f"Sold {amount} shares of {stockname} for {total}, total Sunlight: {balance}")

@bot.tree.command(guild=guild)
async def resetstocks(interaction):
    """resets the stock market"""
    if interaction.user.name != ADMIN:
        await interaction.response.send_message("Admin only")
        return
    with open('stocks.json') as f:
        stocks = json.load(f)
    for stock in stocks:
        stock['price'] = 3
        stock['favorlvl'] = 'neutral'
    with open('stocks.json', 'w') as f:
        json.dump(stocks, f, indent=2)
    investors = [{"name": user.name, "stocks": []} for user in interaction.guild.members]
    with open('user-stocks.json', 'w') as f:
        json.dump(investors, f, indent=2)
    await interaction.response.send_message("Stock market reset :(")
    
# @bot.tree.command(guild=guild)
# async def say(interaction):
#     """mocks you"""
#     print(interaction.user.id)
#     await interaction.response.send_message(interaction.user.id)

def main():
    bot.run(TOKEN)

if __name__ == "__main__":
    main()