import nextcord
import openai
import json
from nextcord.ext import commands
from src.lang_processing import is_english, preprocess_message, should_translate
from main import TRANSLATOR_MODEL
from src.utils import update_guilds
import logging

class AppCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logging.info("AppCommands cog initialized")
        print("AppCommands cog initialized")  # Add this line back

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("app commands live")
        print("app commands live")  # Add this line for consistency

    ################################
    # ADMIN COMMANDS SSHIFT DAO ONLY
    ################################

    @nextcord.slash_command(name="admin", description="Admin functions.", guild_ids=[1098355558022656091])
    async def admin(self, interaction: nextcord.Interaction):
        # Check if the user has the 'administrator' permission in the guild
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have the required permissions to use this command.", ephemeral=True)
            return
    
        try:
            logging.info(f"/admin command invoked by {interaction.user.name} ({interaction.user.id})")
            pass  # This will never get called since it has subcommands.
        except Exception as e:
            logging.error(f"Error executing /admin command: {e}")

    @admin.subcommand(name="add_guild", description="Add a new guild to the allowed list")
    async def add_guild(self, interaction: nextcord.Interaction, guild_name: str, guild_id: str):
        # Convert guild_id to an integer
        try:
            guild_id_int = int(guild_id)
        except ValueError:
            await interaction.response.send_message("Invalid guild ID provided. Please ensure it's a valid number.")
            return
    
        # Read the current list of guilds from the JSON file
        with open("json/member_guilds.json", "r") as file:
            guilds = json.load(file)
    
        # Check if the guild_id already exists
        if any(guild["guild_id"] == guild_id_int for guild in guilds):
            await interaction.response.send_message(f"Guild with ID {guild_id} already exists in the list!")
            return
    
        # Append the new guild data
        guilds.append({
            "guild_id": guild_id_int,
            "guild_name": guild_name
        })
    
        # Write the updated list back to the JSON file
        with open("json/member_guilds.json", "w") as file:
            json.dump(guilds, file, indent=4)
    
        await interaction.response.send_message(f"Guild {guild_name} with ID {guild_id} has been added!")
        await update_guilds()
    
    @admin.subcommand(name="remove_guild", description="Remove a guild from the allowed list")
    async def remove_guild(self, interaction: nextcord.Interaction, guild_id: str):
        # Convert guild_id to an integer
        try:
            guild_id_int = int(guild_id)
        except ValueError:
            await interaction.response.send_message("Invalid guild ID provided. Please ensure it's a valid number.")
            return
    
        # Read the current list of guilds from the JSON file
        with open("json/member_guilds.json", "r") as file:
            guilds = json.load(file)
    
        # Check if the guild_id exists
        guild_to_remove = next((guild for guild in guilds if guild["guild_id"] == guild_id_int), None)
    
        if not guild_to_remove:
            await interaction.response.send_message(f"Guild with ID {guild_id} does not exist in the list!")
            return
    
        # Remove the guild data
        guilds.remove(guild_to_remove)
    
        # Write the updated list back to the JSON file
        with open("json/member_guilds.json", "w") as file:
            json.dump(guilds, file, indent=4)
    
        await interaction.response.send_message(f"Guild with ID {guild_id} has been removed!")
        await update_guilds()


    #################
    # USER COMMANDS
    #################

    @nextcord.slash_command(name="reply", description="Reply to a user's last message.")
    async def reply(self, interaction: nextcord.Interaction, user: nextcord.Member, text: str):
        try:
            logging.info("Received /reply command.")
            await interaction.response.defer()
            processing_msg = await interaction.followup.send("Processing your translation request...")

            messages = await interaction.channel.history(limit=50).flatten()

            user_message = None
            for msg in messages:
                if msg.author == user:
                    cleaned_msg = await preprocess_message(msg.content)
                    if await should_translate(cleaned_msg) and not await is_english(cleaned_msg):
                        user_message = msg
                        break

            if not user_message:
                await interaction.followup.send("Couldn't find a recent non-English message from the selected user that should be translated.")
                return

            original_content = user_message.content
            system_prompt = (
                "Translate the reply to match the language and style of the original message."
            )
            chat_message = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Original message: '{original_content}'. Reply: '{text}'."}
            ]

            response = openai.ChatCompletion.create(
                model=TRANSLATOR_MODEL,
                messages=chat_message,
                temperature=0.2,
                max_tokens=500,
                frequency_penalty=0.0
            )
            translation = response['choices'][0]['message']['content'].strip()

            response_message = f"{interaction.user.mention} replied:\n\n**Original:** {text}\n\n**Translation:** {translation}"
            await user_message.reply(response_message)

            await processing_msg.delete()
        except Exception as e:
            logging.error(f"Error executing /reply command: {e}")


def setup(bot):
    bot.add_cog(AppCommands(bot))
    logging.info("AppCommands cog loaded")
    print("AppCommands cog loaded")
