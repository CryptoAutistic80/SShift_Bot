from database.database_manager import retrieve_active_subscriptions
from nextcord.ext import commands
from src.utils import MEMBER_GUILDS  # Updated import statement

class MembershipManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("MembershipManager: on_ready called")  # Debugging output
        await self.update_allowed_guilds()

    async def update_allowed_guilds(self):
        allowed_guilds = await retrieve_active_subscriptions()
        print(f"MembershipManager: allowed_guilds = {allowed_guilds}")  # Debugging output
        MEMBER_GUILDS.update(allowed_guilds)  # Update the global MEMBER_GUILDS list using the update method

def setup(bot):
    bot.add_cog(MembershipManager(bot))
    print("MembershipManager cog loaded")

