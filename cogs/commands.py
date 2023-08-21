import nextcord
import logging
from nextcord.ext import commands
from database.database_manager import retrieve_translation_by_original_message_id
import asyncio


class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logging.info("CommandsCog initialized")
        print("CommandsCog cog initialized")

    @commands.Cog.listener()
    async def on_ready(self):
      print("Commands Loaded")

    @commands.command(name="fetch", help="Fetch the translation for a replied message")
    async def fetch_command(self, ctx):
        """Fetch the translation for a replied message using traditional command"""
        logging.info(f"!fetch command invoked by {ctx.author.name} ({ctx.author.id})")
        # Check if the context is in reply to an existing message
        if ctx.message.reference:
            original_message_id = ctx.message.reference.message_id
            # Fetch the translation from the database
            translation = await retrieve_translation_by_original_message_id(original_message_id)
            # If a translation exists, send it
            if translation:
                msg = await ctx.send(translation)
            else:
                msg = await ctx.send(f"No translation found for message ID {original_message_id}")
            
            # Set a timer to delete the response and the !fetch command message after 2 minute
            await asyncio.sleep(120)  # Wait for 120 seconds
            await msg.delete()
            await ctx.message.delete()
    
        else:
            await ctx.send("Please reply to a message to fetch its translation.")
        
    
def setup(bot):
    bot.add_cog(CommandsCog(bot))
    print("Command Cog loaded")
    logging.info("CommandsCog has been loaded")
