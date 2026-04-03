import discord
import os 
import random
import requests
import json
from pathlib import Path
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from datetime import time, datetime
from sqlalchemy import select, exists, func

from database import get_db, Base, engine
from Utils.TaskManager import TaskManager
from Utils.Time import discord_time
from Utils.DependInject import inject, Depends
from Utils.WaifuNums import WaifuType
from Utils.Roles import Roles

#for database creation and other usage
from Entities.Users import User
from Entities.Tasks import Task
from Entities.Quotes import Quote

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
            role=Roles.USER if int(discord_id) != ADMIN else Roles.ADMIN
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
    
@inject
async def seed_quotes(data, db = Depends(get_db)):
    notempty = db.scalar(
        select(exists().where(Quote.id != None))
    )
    if notempty:
        return
    for seedquote in data:
        newquote = Quote(
            content=seedquote["content"],
            author_id=seedquote["author_id"]
        )
        db.add(newquote)
    db.commit()

async def seed_data():
    seeded_data_dir = Path("./SeededData")
    for filepath in seeded_data_dir.glob("*.json"):
        with open(filepath) as f:
            data = json.load(f)
        match filepath.name.split(".")[0]:
            case Quote.__tablename__:
                await seed_quotes(data)
            case _:
                continue

#events-------------------------------------------------------------------------------------------------------------

@bot.event
@inject
async def on_ready(db = Depends(get_db)):
    await TaskManager.syncdb()
    TaskManager.startall()
    await TaskManager.wait_until_ready()
    global general
    general = await bot.fetch_channel(CID)
    for user in bot.guilds[0].members: #this assumes the bot is in only one guild
        indb = db.scalar(
            select(exists().where(User.id == user.id))
        )
        if indb:
            continue
        newuser = User(
            id=user.id,
            username=user.display_name,
            role=Roles.USER if int(user.id) != ADMIN else Roles.ADMIN
        )
        db.add(newuser)
    db.commit()
    await seed_data()
    await TaskManager.run("test")

@bot.event
@inject
async def on_member_update(before, after, db = Depends(get_db)):
    if before.nick != after.nick:
        user = db.execute(
            select(User).where(User.id == after.id)
        ).scalar_one_or_none()
        user.username = after.nick
        db.commit()

@bot.event
@inject
async def on_member_join(member, db = Depends(get_db)):
    newuser = User(
        id=member.id,
        username=member.nick,
        role=Roles.User if int(member.id) != ADMIN else Roles.ADMIN
    )
    db.add(newuser)
    db.commit()
    await general.send(f"Welcome to the server {member.nick}! Enjoying the sunlight?")

#tasks--------------------------------------------------------------------------------------------------------------

@TaskManager.register("test", time=time(hour=15, minute=0))
async def test():
    print("yamomma")

task_group = app_commands.Group(name="task", description="commands for tasks (admin only)")

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

@task_group.command()
@app_commands.autocomplete(taskname=taskname_autocomplete)
@inject
async def run(interaction, taskname: str, admin = Depends(require_admin)):
    """Runs a task immediately."""
    if taskname not in TaskManager.tasks.keys():
        await interaction.response.send_message("Task not found.", ephemeral=True)
        return
    if not TaskManager.tasks[taskname]["enabled"]:
        await interaction.response.send_message(f"Task: {taskname} is disabled.", ephemeral=True)
        return
    await TaskManager.run(taskname)
    await interaction.response.send_message(f"Ran task {taskname}.", ephemeral=True)

@task_group.command()
@app_commands.autocomplete(taskname=taskname_autocomplete)
@inject
async def disable(interaction, taskname: str, admin = Depends(require_admin)):
    """Disables a task."""
    if taskname not in TaskManager.tasks.keys():
        await interaction.response.send_message("Task not found.", ephemeral=True)
        return
    await TaskManager.disable(taskname)
    await interaction.response.send_message(f"Disabled task {taskname}.", ephemeral=True)

@task_group.command()
@app_commands.autocomplete(taskname=taskname_autocomplete)
@inject
async def enable(interaction, taskname: str, admin = Depends(require_admin)):
    """Enables a task."""
    if taskname not in TaskManager.tasks.keys():
        await interaction.response.send_message("Task not found.", ephemeral=True)
        return
    await TaskManager.enable(taskname)
    await interaction.response.send_message(f"Enabled task {taskname}.", ephemeral=True)

bot.tree.add_command(task_group, guild=guild)

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

@bot.tree.command(guild=guild)
@inject
async def quote(interaction, author: discord.User = None, private: bool = True, db = Depends(get_db)):
    """Shows a random quote"""
    if author:
        stmt = select(Quote).where(Quote.author_id == author.id).order_by(func.random()).limit(1)
    else:
        stmt = select(Quote).order_by(func.random()).limit(1)
    quote = db.scalar(stmt)
    await interaction.response.send_message(f"{quote.content}\n\t- {quote.author.username}", ephemeral=private)

@bot.tree.context_menu(name="Create Quote", guild=guild)
@inject
async def create_quote(interaction: discord.Interaction, message: discord.Message, db = Depends(get_db)):
    """Creates a quote from a message"""
    newquote = Quote(
        content=message.content,
        author_id=message.author.id
    )
    db.add(newquote)
    db.commit()
    await interaction.response.send_message(f"Ahh, dear adventurer! '{newquote.content}'? A most radiant notion, spoken by a wise sage of another age! Truly, even in our darkest hours, the sun yet burns above! Never forget—there is glory in perseverance, and splendor in struggle. Praise the Sun! 🌞")

#Running------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    bot.run(TOKEN)