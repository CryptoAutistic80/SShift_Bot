import os
import nextcord
from nextcord.ext import commands

# Import the start_server function from your FastAPI file
from server import start_server

# Create an Intents object with all intents enabled
intents = nextcord.Intents.all()

# Initialize the bot with the enabled intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Load all cogs in the cogs directory
for cog_name in os.listdir('./cogs'):
    if cog_name.endswith('.py'):
        bot.load_extension(f'cogs.{cog_name[:-3]}')

# Start the FastAPI server to keep the Replit project awake
start_server()

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))


