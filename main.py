import os
import nextcord
import logging
import logging.handlers
from nextcord.ext import commands

# Import the start_server function from your FastAPI file and the TRANSLATE_CONFIG from config.py
from server import start_server
from config import TRANSLATE_CONFIG
from database.database_manager import initialize_db

# Logging setup
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(filename='discord.log', encoding='utf-8', maxBytes=10**7, backupCount=5)
console_handler = logging.StreamHandler()
fmt = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
handler.setFormatter(fmt)
console_handler.setFormatter(fmt)
logger.addHandler(handler)
logger.addHandler(console_handler)

# Create an Intents object with all intents enabled
intents = nextcord.Intents.all()

# Initialize the bot with the enabled intents
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}!')
    await initialize_db()
    
    logger.info("About to load extensions.")
    
    loaded_cogs = set()  # To keep track of which cogs are already loaded

    for guild in bot.guilds:
        logger.info(f"Bot is in guild: {guild.name} ({guild.id})")
        if guild.id in TRANSLATE_CONFIG and 'cogs.translator' not in loaded_cogs:
            logger.info(f"Loading extensions for guild: {guild.name} ({guild.id})")
            bot.load_extension('cogs.translator')
            loaded_cogs.add('cogs.translator')

# Start the FastAPI server to keep the Replit project awake
start_server()

# Load the cogs.commands extension before the bot runs
bot.load_extension('cogs.commands')
bot.run(os.getenv('DISCORD_TOKEN'))








