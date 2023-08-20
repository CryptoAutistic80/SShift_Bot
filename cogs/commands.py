import nextcord
import logging
from nextcord.ext import commands
from database.database_manager import retrieve_translation_by_original_message_id
import asyncio


class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logging.info("CommandsCog initialized")

  

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
            
            # Set a timer to delete the response and the !fetch command message after 1 minute
            await asyncio.sleep(30)  # Wait for 30 seconds
            await msg.delete()
            await ctx.message.delete()
    
        else:
            await ctx.send("Please reply to a message to fetch its translation.")
          

  
    @nextcord.slash_command(name="get", description="Fetch the translation for a replied message")
    async def get(self, interaction: nextcord.Interaction, 
                  option: str = nextcord.SlashOption(
                      choices={"Translation": "translation"},
                      description="Select an option to fetch"),
                  ):
        """Fetch the translation for a replied message using slash command"""
        logging.info(f"/get command invoked by {interaction.user.name} ({interaction.user.id})")
        # Check if the interaction is in reply to an existing message
        if interaction.message.reference:
            original_message_id = interaction.message.reference.message_id
            # Fetch the translation from the database
            retrieved_translation = await retrieve_translation_by_original_message_id(original_message_id)
            # If a translation exists, send it
            if retrieved_translation:
                await interaction.response.send_message(retrieved_translation, ephemeral=True)
            else:
                await interaction.response.send_message(f"No translation found for message ID {original_message_id}", ephemeral=True)
        else:
            await interaction.response.send_message("Please reply to a message to fetch its translation.", ephemeral=True)



def setup(bot):
    bot.add_cog(CommandsCog(bot))
    print("Command Cog loaded")
    logging.info("CommandsCog has been loaded")
