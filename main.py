import nextcord
import logging
import logging.handlers
import os
from nextcord.ext import commands
from server import start_server
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
    load_cogs()

def load_cogs():
    """Function to load all cogs from the cogs directory."""
    # Import necessary libraries for directory navigation
    import os
    
    cogs_directory = "cogs"
    
    # Iterate through each file in the cogs directory
    for filename in os.listdir(cogs_directory):
        # If the file ends with .py, it's potentially a cog
        if filename.endswith(".py"):
            cog_path = f"{cogs_directory}.{filename[:-3]}"  # Removes the .py extension
            try:
                bot.load_extension(cog_path)
                logger.info(f"Loaded cog: {cog_path}")
            except Exception as e:
                logger.error(f"Failed to load cog: {cog_path}. Error: {e}")

# Start the FastAPI server to keep the Replit project awake
start_server()

bot.run(os.getenv('DISCORD_TOKEN'))
