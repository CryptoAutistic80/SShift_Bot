import nextcord
from database.database_manager import retrieve_translation

class TranslationButton(nextcord.ui.Button):
    def __init__(self, message_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_id = message_id

    async def callback(self, interaction: nextcord.Interaction):
        try:
            await interaction.response.defer()
            translation = await retrieve_translation(interaction.guild.id, str(self.message_id))
            if not translation:
                translation = "Translation not found."
            await interaction.followup.send(translation, ephemeral=True)
        except Exception:
            await interaction.followup.send("An error occurred while processing the request.", ephemeral=True)

class TranslationView(nextcord.ui.View):
    def __init__(self, cog, message_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cog = cog
        self.add_item(TranslationButton(message_id, label="Analysing...", style=nextcord.ButtonStyle.grey, disabled=True))
