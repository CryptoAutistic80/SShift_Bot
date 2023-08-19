import os
import nextcord
from nextcord.ext import commands

# Import the start_server function from your FastAPI file and the TRANSLATE_CONFIG from config.py
from server import start_server
from config import TRANSLATE_CONFIG
from database.database_manager import initialize_db

# Create an Intents object with all intents enabled
intents = nextcord.Intents.all()

# Initialize the bot with the enabled intents
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}!')
    await initialize_db()
    
    # Load cogs based on TRANSLATE_CONFIG
    for guild in bot.guilds:
        if guild.id in TRANSLATE_CONFIG:
            bot.load_extension('cogs.translator')
            bot.load_extension('cogs.commands')
            break  # Exit loop once the translator cog is loaded

# Start the FastAPI server to keep the Replit project awake
start_server()

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))






