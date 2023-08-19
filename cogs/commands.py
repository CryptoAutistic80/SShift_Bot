import nextcord
from nextcord.ext import commands
from database.database_manager import retrieve_translation_by_original_message_id

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fetch", help="Fetch the translation for a replied message")
    async def fetch(self, ctx):
        # Check if the context is in reply to an existing message
        if ctx.message.reference:
            original_message_id = ctx.message.reference.message_id
            # Fetch the translation from the database
            translation = retrieve_translation_by_original_message_id(original_message_id)
            # If a translation exists, send it
            if translation:
                await ctx.send(translation)

def setup(bot):
    bot.add_cog(CommandsCog(bot))
    print("Commands cog loaded")