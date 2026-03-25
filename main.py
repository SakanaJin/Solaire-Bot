import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
from datetime import time, datetime

from database import get_db, Base, engine
from Utils.TaskManager import TaskManager
from Utils.Time import discord_time

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
    with get_db() as db:
        await TaskManager.syncdb(db)
    TaskManager.startall()
    await TaskManager.wait_until_ready()
    await TaskManager.run("test")

#tasks--------------------------------------------------------------------------------------------------------------

@TaskManager.register("test", time=time(hour=15, minute=0))
async def test():
    print("gay")

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
        if loop.is_running():
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

#basic commands-----------------------------------------------------------------------------------------------------

@bot.command()
async def sync(ctx):
    """syncs commands"""
    if ctx.author.id != ADMIN:
        await ctx.send("Admin only")
        return
    await bot.tree.sync(guild=guild)

#utility------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    bot.run(TOKEN)