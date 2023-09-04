import json
import logging

logger = logging.getLogger('discord')

def get_member_guilds():
    """Load guilds from the member_guilds.json file."""
    with open('json/member_guilds.json', 'r') as f:
        guilds_data = json.load(f)
    return [guild['guild_id'] for guild in guilds_data]

async def update_guilds():
    global MEMBER_GUILDS
    logger.info("Updating MEMBER_GUILDS...")
    MEMBER_GUILDS = get_member_guilds()
    logger.info("MEMBER_GUILDS has been updated.")
