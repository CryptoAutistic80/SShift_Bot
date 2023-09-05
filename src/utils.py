import logging

logger = logging.getLogger('discord')

class MemberGuilds:
    def __init__(self):
        self.guild_list = []

    def update(self, new_list):
        self.guild_list = new_list
        print(f"utils.py: MEMBER_GUILDS updated: {self.guild_list}")  # Add this line to check the update

    def get(self):
        return self.guild_list

# Create a single instance of MemberGuilds
MEMBER_GUILDS = MemberGuilds()




