import discord
import os 
import random
import requests
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from datetime import time, datetime
from sqlalchemy import select

from database import get_db, Base, engine
from Utils.TaskManager import TaskManager
from Utils.Time import discord_time
from Utils.DependInject import inject, Depends
from Utils.WaifuNums import WaifuType
from Utils.Roles import Roles

#for database creation and other usage
from Entities.Users import User
from Entities.Tasks import Task

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CID = os.getenv('CID')
GID = os.getenv('GID')
ADMIN = int(os.getenv('ADMIN'))
MEMEAPIURL = "https://meme-api.com"
WAIFUAPIURL = "https://api.waifu.pics"
HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
general = None
guild = discord.Object(id=GID)

#utility------------------------------------------------------------------------------------------------------------

class AdminOnly(Exception):
    pass

@inject
async def get_current_user(interaction: discord.Interaction, db = Depends(get_db)):
    discord_id = interaction.user.id
    user = db.execute(
        select(User).where(User.id == discord_id)
    ).scalar_one_or_none()
    if not user:
        user = User(
            id=discord_id,
            username=interaction.user.display_name,
            role=Roles.USER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@inject
async def require_admin(interaction: discord.Interaction, user = Depends(get_current_user)):
    if user.role != Roles.ADMIN:
        await interaction.response.send_message("Admin only", ephemeral=True)
        raise AdminOnly()
    else:
        return user

#events-------------------------------------------------------------------------------------------------------------

@bot.event
async def on_ready():
    await TaskManager.syncdb()
    TaskManager.startall()
    await TaskManager.wait_until_ready()
    await TaskManager.run("test")
    #check if all users are in db

#tasks--------------------------------------------------------------------------------------------------------------

@TaskManager.register("test", time=time(hour=15, minute=0))
async def test():
    print("yamomma")

async def taskname_autocomplete(interaction, current):
    choices = []
    for task in TaskManager.tasks.keys():
        if current.lower() in task.lower():
            choices.append(app_commands.Choice(name=task, value=task))
    return choices

@bot.tree.command(guild=guild)
async def tasks(interaction: discord.Interaction):
    """Shows task dashboard"""
    tasks = TaskManager.tasks
    sorted_tasks = sorted(
        tasks.items(),
        key=lambda x: x[1]["task"].next_iteration or datetime.max
    )
    embed = discord.Embed(
        title="Task Dashboard",
        color=discord.Color.blurple()
    )
    for name, task in sorted_tasks:
        loop = task["task"]
        status = "[X]"
        if task["enabled"]:
            status = "[O]"
        next_run = discord_time(loop.next_iteration)
        meat = (
            f"Status: {status}\n"
            f"Enabled: `{task["enabled"]}`\n"
            f"Scheduled: {next_run}"
        )
        embed.add_field(
            name=name,
            value=meat,
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(guild=guild)
@app_commands.autocomplete(taskname=taskname_autocomplete)
async def runtask(interaction, taskname: str):
    #add admin check later
    if taskname not in TaskManager.tasks.keys():
        await interaction.response.send_message("Task not found.", ephemeral=True)
        return
    if not TaskManager.tasks[taskname]["enabled"]:
        await interaction.response.send_message(f"Task: {taskname} is disabled.", ephemeral=True)
        return
    await TaskManager.run(taskname)
    await interaction.response.send_message(f"Ran task {taskname}.", ephemeral=True)

@bot.tree.command(guild=guild)
@app_commands.autocomplete(taskname=taskname_autocomplete)
async def disabletask(interaction, taskname: str):
    #add admin check later
    if taskname not in TaskManager.tasks.keys():
        await interaction.response.send_message("Task not found.", ephemeral=True)
        return
    await TaskManager.disable(taskname)
    await interaction.response.send_message(f"Disabled task {taskname}.", ephemeral=True)

@bot.tree.command(guild=guild)
@app_commands.autocomplete(taskname=taskname_autocomplete)
async def enabletask(interaction, taskname: str):
    #add admin check later
    if taskname not in TaskManager.tasks.keys():
        await interaction.response.send_message("Task not found.", ephemeral=True)
        return
    await TaskManager.enable(taskname)
    await interaction.response.send_message(f"Enabled task {taskname}.", ephemeral=True)

#basic commands-----------------------------------------------------------------------------------------------------

@bot.command()
async def sync(ctx):
    """syncs commands"""
    if ctx.author.id != ADMIN:
        await ctx.send("Admin only")
        return
    await bot.tree.sync(guild=guild)

@bot.tree.command(guild=guild)
@inject
async def test(interaction, db = Depends(get_db)):
    task = db.execute(
        select(Task)
        .where(Task.id == 1)
    ).scalar_one_or_none()
    await interaction.response.send_message(f"Task with id=1: {task.name}")

@bot.tree.command(guild=guild)
async def flip(interaction, private: bool = False):
    """flips a coin"""
    await interaction.response.send_message(["heads", "tails"][random.randint(0,1)], ephemeral=private)

@bot.tree.command(guild=guild)
async def rolld(interaction, sides: int = 6, private: bool = False):
    """rolls an n sided dice (default six sided)"""
    await interaction.response.send_message(random.randint(1, sides), ephemeral=private)

@bot.tree.command(guild=guild)
async def meme(interaction, private: bool = True):
    """Solaire personally bestows upon you a meme"""
    response = requests.get(MEMEAPIURL + "/gimme")
    imgurl = response.json()["url"]
    await interaction.response.send_message(imgurl, ephemeral=private)

@bot.tree.command(guild=guild)
async def berserk(interaction, private: bool = True):
    """berk"""
    response = requests.get(MEMEAPIURL + "/gimme/berserk")
    imgurl = response.json()["url"]
    await interaction.response.send_message(imgurl, ephemeral=private)

async def waifutype_autocomplete(interaction, current):
    return [
        app_commands.Choice(name=choice, value=choice)
        for choice in WaifuType if current.lower() in choice.lower()
    ]

@bot.tree.command(guild=guild)
@app_commands.autocomplete(type=waifutype_autocomplete)
async def waifu(interaction, type: str = WaifuType.SFW.value, category: str = "waifu", private: bool = True):
    """Throws a waifu"""
    if type == "n":
        type = WaifuType.NSFW
    response = requests.get(WAIFUAPIURL + f"/{type}/{category}")
    imgurl = response.json()['url']
    await interaction.response.send_message(imgurl, ephemeral=private)

@bot.tree.command(guild=guild)
async def traumatize(interaction):
    """Traumatize nearest viewer"""
    source = requests.get(f"https://e621.net/posts?page={random.randint(1,21)}&tags=hi_res+why", headers=HEADERS)
    soup = BeautifulSoup(source.text, 'html.parser')
    Images = soup.find_all('img')
    img_links=[image['src'] for image in Images]
    await interaction.response.send_message(img_links[random.randint(2,65)])

@bot.tree.command(guild=guild)
@inject
async def balance(interaction, user = Depends(get_current_user)):
    """Shows current Sunlight"""
    await interaction.response.send_message(f"Sunlight: {user.sunlight:,}", ephemeral=True)

@bot.tree.command(guild=guild)
@inject
async def whosagoodboy(interaction, goodboy: discord.User, money: int, db = Depends(get_db), admin = Depends(require_admin)):
    """You are yes you are :3"""
    #add admin check
    try:
        user = db.execute(
            select(User)
            .where(User.id == goodboy.id)
        ).scalar_one_or_none()
        user.sunlight += money
        db.commit()
        await interaction.response.send_message(f"Ahh, {goodboy}… truly, you are a good boy indeed! Rare is the soul who shines with such brilliance. Take this reward of {money:,} Sunlight — a symbol of my esteem. May it guide you ever closer to your own sun!")
    except:
        await interaction.response.send_message("Would result in negative sunlight cancelling", ephemeral=True)

#Running------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    bot.run(TOKEN)