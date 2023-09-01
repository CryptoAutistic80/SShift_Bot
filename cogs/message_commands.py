import nextcord
from nextcord.ext import commands
import logging
from database.database_manager import retrieve_translation_by_original_message_id

class MessageCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("MessageCommands cog initialized")

    @commands.Cog.listener()
    async def on_ready(self):
        print("message commands live")
      
    @nextcord.message_command(name="TRANSLATION")
    async def fetch_translation(self, interaction: nextcord.Interaction, target_message: nextcord.Message):
        """Fetch the translation for a right-clicked (context menu) message"""
        try:
            logging.info(f"fetch_translation message-command invoked by {interaction.user.name} ({interaction.user.id})")
            
            original_message_id = target_message.id
            # Fetch the translation from the database
            retrieved_translation = await retrieve_translation_by_original_message_id(interaction.guild.id, original_message_id)
            
            # If a translation exists, send it
            if retrieved_translation:
                await interaction.response.send_message(retrieved_translation, ephemeral=True)
            else:
                await interaction.response.send_message(f"No translation found for message ID {original_message_id}", ephemeral=True)
        except Exception as e:
            logging.error(f"Error executing fetch_translation message-command: {e}")
            await interaction.response.send_message("An error occurred while fetching the translation.", ephemeral=True)

def setup(bot):
    bot.add_cog(MessageCommands(bot))
    print("MessageCommands cog loaded")
