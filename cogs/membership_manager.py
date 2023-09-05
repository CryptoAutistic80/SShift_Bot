from database.database_manager import retrieve_active_subscriptions
from nextcord.ext import commands, tasks

class MembershipManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_list = []  # Integrated guild_list attribute
        self.update_task = self.update_allowed_guilds.start()  # Start the update task loop
        print("Membership Cog Initilized")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Membership Manager Ready")  # Debugging output

    @tasks.loop(minutes=15)
    async def update_allowed_guilds(self):
        allowed_guilds = await retrieve_active_subscriptions()
        self.update(allowed_guilds)  # Updated method call to use self.update

    def update(self, new_list):  # Integrated update method
        self.guild_list = new_list

    def get(self):  # Integrated get method
        return self.guild_list

    def cog_unload(self):
        self.update_task.cancel()  # Cancel the loop when the cog is unloaded

def setup(bot):
    bot.add_cog(MembershipManager(bot))
    print("Membership Manager cog loaded")
