import nextcord
from nextcord.ext import commands
from database.database_manager import retrieve_translation_by_original_message_id
import logging

class AppCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("AppCommands cog initialized")  # Add this line

    @commands.Cog.listener()
    async def on_ready(self):
        print("/get command live")

    @nextcord.slash_command(name="get", description="Translate a message to English.", guild_ids=[1098355558022656091])
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
    bot.add_cog(AppCommands(bot))
    print("AppCommands cog loaded")

