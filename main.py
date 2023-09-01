# ________  ________      ___    ___ ________  _________  ________          ________  ___  ___  _________  ___  ________  _________  ___  ________         
#|\   ____\|\   __  \    |\  \  /  /|\   __  \|\___   ___\\   __  \        |\   __  \|\  \|\  \|\___   ___\\  \|\   ____\|\___   ___\\  \|\   ____\        
#\ \  \___|\ \  \|\  \   \ \  \/  / | \  \|\  \|___ \  \_\ \  \|\  \       \ \  \|\  \ \  \\\  \|___ \  \_\ \  \ \  \___|\|___ \  \_\ \  \ \  \___|        
# \ \  \    \ \   _  _\   \ \    / / \ \   ____\   \ \  \ \ \  \\\  \       \ \   __  \ \  \\\  \   \ \  \ \ \  \ \_____  \   \ \  \ \ \  \ \  \           
#  \ \  \____\ \  \\  \|   \/  /  /   \ \  \___|    \ \  \ \ \  \\\  \       \ \  \ \  \ \  \\\  \   \ \  \ \ \  \|____|\  \   \ \  \ \ \  \ \  \____      
#   \ \_______\ \__\\ _\ __/  / /      \ \__\        \ \__\ \ \_______\       \ \__\ \__\ \_______\   \ \__\ \ \__\____\_\  \   \ \__\ \ \__\ \_______\    
#    \|_______|\|__|\|__|\___/ /        \|__|         \|__|  \|_______|        \|__|\|__|\|_______|    \|__|  \|__|\_________\   \|__|  \|__|\|_______|    
#                      \|___|/                                                                                   \|_________|                             
                                                                                                                                                          
                                                                                                                                                          
#          ___  _____ ______   ________  ________  ___  ________   _______   _______   ________                                                           
#         |\  \|\   _ \  _   \|\   __  \|\   ____\|\  \|\   ___  \|\  ___ \ |\  ___ \ |\   __  \                                                          
#         \ \  \ \  \\\__\ \  \ \  \|\  \ \  \___|\ \  \ \  \\ \  \ \   __/|\ \   __/|\ \  \|\  \                                                         
#          \ \  \ \  \\|__| \  \ \   __  \ \  \  __\ \  \ \  \\ \  \ \  \_|/_\ \  \_|/_\ \   _  _\                                                        
#           \ \  \ \  \    \ \  \ \  \ \  \ \  \|\  \ \  \ \  \\ \  \ \  \_|\ \ \  \_|\ \ \  \\  \|                                                       
#            \ \__\ \__\    \ \__\ \__\ \__\ \_______\ \__\ \__\\ \__\ \_______\ \_______\ \__\\ _\                                                       
#             \|__|\|__|     \|__|\|__|\|__|\|_______|\|__|\|__| \|__|\|_______|\|_______|\|__|\|__|    
#
# SShift DAO - 2023 
# http://www.sshift.xyz
#
import nextcord
import logging
import logging.handlers
import os
import openai
import json
from nextcord.ext import commands, tasks
from server import start_server
from database.database_manager import initialize_db

# Initialize the OpenAI API
openai.api_key = os.environ['Key_OpenAI']

# Set Constants
TRANSLATOR_MODEL = "gpt-3.5-turbo"

def get_member_guilds():
    """Load guilds from the member_guilds.json file."""
    with open('json/member_guilds.json', 'r') as f:
        guilds_data = json.load(f)
    return [guild['guild_id'] for guild in guilds_data]

MEMBER_GUILDS = get_member_guilds()

def setup_logging():
    """Configure logging for the bot."""
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    
    handler = logging.handlers.RotatingFileHandler(filename='discord.log', encoding='utf-8', maxBytes=10**7, backupCount=5)
    console_handler = logging.StreamHandler()
    
    fmt = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    handler.setFormatter(fmt)
    console_handler.setFormatter(fmt)
    
    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger

def load_cogs(bot, logger):
    """Load all cogs from the cogs directory."""
    cogs_directory = "cogs"
    
    for filename in os.listdir(cogs_directory):
        if filename.endswith(".py"):
            cog_path = f"{cogs_directory}.{filename[:-3]}"  # Removes the .py extension
            try:
                bot.load_extension(cog_path)
                logger.info(f"Loaded cog: {cog_path}")
            except Exception as e:
                logger.error(f"Failed to load cog: {cog_path}. Error: {e}")

# Set up logging
logger = setup_logging()

# Create an Intents object with all intents enabled
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}!')
    await initialize_db()

# Load cogs
load_cogs(bot, logger)

# Start the FastAPI server to keep the Replit project awake
start_server()

@tasks.loop(minutes=15)  # This will refresh every 15 minutes. Adjust as needed.
async def update_guilds():
    global MEMBER_GUILDS
    logging.info("Starting the update_guilds task...")
    MEMBER_GUILDS = get_member_guilds()
    logging.info("MEMBER_GUILDS has been updated.")

@update_guilds.before_loop
async def before_update_guilds():
    logging.info("Waiting for the bot to be ready before starting the update_guilds task...")
    await bot.wait_until_ready()
    logging.info("Bot is ready. The update_guilds task will now start.")

update_guilds.start()

# Start the bot
bot.run(os.getenv('DISCORD_TOKEN'))
