import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import requests
from bs4 import BeautifulSoup
import json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CID = os.getenv('CID')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

headsortails = ["heads", "tails"]
headers = headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

#events----------------------------------------------------------------------------------------------

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord")
    await send_to_general("Solaire is back basking in the sunlight!")

@bot.event
async def on_member_join(member):
    with open('data.json') as f:
        data = json.load(f)
    data.append({"name": str(member.name), "fucks": 0})
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await send_to_general(f"Welcome to the server {member.name}! Enjoying the sunlight?")

async def send_to_general(msg):
    try:
        channel = bot.get_channel(CID)
        await channel.send(msg)
    except Exception as e:
        print(e)

#on message---------------------------------------------------------------------------------------------

@bot.event
async def on_message(msg):
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

@bot.command()
async def test(ctx):
    """:3"""
    await ctx.send("Working")

@bot.command()
async def flip(ctx):
    """flips a coin"""
    await ctx.send(f"{headsortails[random.randint(0,1)]}")

@bot.command()
async def roll(ctx):
    """roll d6"""
    await ctx.send(f"{random.randint(1,6)}")

@bot.command()
async def rolld(ctx, *, msg):
    """rolls blank sided die"""
    try:
        num = int(msg)
        await ctx.send(f"{random.randint(1,num)}")
    except Exception as e:
        await ctx.send(f"{e}")

@bot.command()
async def meme(ctx):
    """funee"""
    response = requests.get("https://meme-api.com/gimme")
    imgurl = response.json()['url']
    await ctx.send(imgurl)

@bot.command()
async def berserk(ctx):
    """berk"""
    response = requests.get("https://meme-api.com/gimme/berserk")
    imgurl = response.json()['url']
    await ctx.send(imgurl)

@bot.command()
async def waifu(ctx, *, msg="waifu"):
    """throws a waifu with args"""
    try:
        msg = msg.lower()
        if "-n" in msg:
            type = "nsfw"
            msg = msg.replace('-n', '')
            msg = msg.replace(' ', '')
            if msg == '':
                msg = "waifu"
        else:
            type = "sfw"
        response = requests.get("https://api.waifu.pics/" + type + '/' + msg)
        imgurl = response.json()['url']
        await ctx.send(imgurl)
    except Exception as e:
        await ctx.send("Not a valid category")

@bot.command()
async def traumatize(ctx):
    """truamatizes nearest viewer"""
    source = requests.get("https://e621.net/posts?tags=hi_res+", headers = headers)
    soup = BeautifulSoup(source.text, 'html.parser')
    Images = soup.find_all('img')
    img_links=[]
    for image in Images:
        img_links.append(image['src'])
    image = img_links[5]
    await ctx.send(image)

@bot.command()
async def fricks(ctx):
    """fucks stats"""
    message = ""
    with open('data.json') as f:
        data = json.load(f)
    data = sorted(data, key=lambda user: user['fucks'], reverse=True)
    for user in data:
        message = message + f"{user['name']}: {user['fucks']}\n"
    print(message)
    await ctx.send(message)

@bot.command()
async def resetdata(ctx):
    """resets data.json"""
    data = [{"name": str(user), "fucks": 0} for user in ctx.channel.members]
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    await ctx.send("data reset")

def main():
    bot.run(TOKEN)

if __name__ == "__main__":
    main()