import nextcord
from nextcord.ext import commands
import logging

class AppCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("AppCommands cog initialized")  # Add this line

    @commands.Cog.listener()
    async def on_ready(self):
        print("/admin command live")

    @nextcord.slash_command(name="admin", description="Admin functions.", guild_ids=[1098355558022656091])
    async def admin(self, interaction: nextcord.Interaction):
        """Admin functions coming soon."""
        logging.info(f"/admin command invoked by {interaction.user.name} ({interaction.user.id})")
        await interaction.response.send_message("Coming Soon", ephemeral=True)
    
def setup(bot):
    bot.add_cog(AppCommands(bot))
    print("AppCommands cog loaded")


