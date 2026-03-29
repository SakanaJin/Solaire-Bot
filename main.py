import discord
import os 
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from datetime import time, datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from functools import wraps

from database import get_db, Base, engine, get_database
from Utils.TaskManager import TaskManager
from Utils.Time import discord_time
from Utils.DependInject import inject, Depends

#for database creation and other usage
from Entities.Users import User
from Entities.Tasks import Task

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CID = os.getenv('CID')
GID = os.getenv('GID')
ADMIN = int(os.getenv('ADMIN'))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
general = None
guild = discord.Object(id=GID)

#events-------------------------------------------------------------------------------------------------------------

@bot.event
async def on_ready():
    await TaskManager.syncdb()
    TaskManager.startall()
    await TaskManager.wait_until_ready()
    await TaskManager.run("test")

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

#utility------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    bot.run(TOKEN)