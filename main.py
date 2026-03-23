import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORN_TOKEN')
CID = os.getenv('CID')
GID = os.getenv('GID')
ADMIN = int(os.getenv('ADMIN'))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
general = None
guild = discord.Object(id=GID)

if __name__ == "__main__":
    bot.run(TOKEN)