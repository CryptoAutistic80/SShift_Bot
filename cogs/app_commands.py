import nextcord
import openai
from nextcord.ext import commands
from nextcord import SlashOption
from src.lang_processing import is_english, preprocess_message, should_translate
from database.database_manager import add_guild as db_add_guild, remove_guild as db_remove_guild, retrieve_guild_membership
from main import TRANSLATOR_MODEL
from src.utils import update_guilds
import time
from datetime import datetime
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
    async def add_guild(
        self, 
        interaction: nextcord.Interaction, 
        guild_name: str, 
        guild_id: str, 
        days_subscribed: int, 
        membership_type: str = SlashOption(
            name="membership_type",
            choices={"Basic": "basic", "Premium": "premium", "Free Trial": "free trial"},
        ),
        Subscription_Active: str = SlashOption(
            name="subscription_status",
            choices={"Yes": "yes", "No": "no"},
        )
    ):
        # Convert guild_id to an integer
        try:
            guild_id_int = int(guild_id)
        except ValueError:
            await interaction.response.send_message("Invalid guild ID provided. Please ensure it's a valid number.")
            return
    
        # Get the current timestamp and calculate the expiration timestamp
        try:
            current_timestamp = int(time.time())
            expiration_timestamp = current_timestamp + (days_subscribed * 86400)  # 86400 seconds in a day
        except ValueError:
            await interaction.response.send_message("Invalid number of days provided. Please ensure it's a valid number.")
            return
    
        # Use the add_guild function to add the guild to the database or get an error message if it already exists
        response = await db_add_guild(guild_id_int, guild_name, membership_type, expiration_timestamp, Subscription_Active)
        await interaction.response.send_message(response)
     
    @admin.subcommand(name="remove_guild", description="Remove a guild from the allowed list")
    async def remove_guild(self, interaction: nextcord.Interaction, guild_id: str):
        # Convert guild_id to an integer
        try:
            guild_id_int = int(guild_id)
        except ValueError:
            await interaction.response.send_message("Invalid guild ID provided. Please ensure it's a valid number.")
            return
        
        # Use the remove_guild function from database_manager to remove the guild from the database
        response = await db_remove_guild(guild_id_int)
        
        # Send the feedback to the user
        await interaction.response.send_message(response)

    @admin.subcommand(name="get_guild_info", description="Retrieve a guild's membership details")
    async def get_guild_info(
        self, 
        interaction: nextcord.Interaction, 
        guild_id: str
    ):
        # Convert guild_id to an integer
        try:
            guild_id_int = int(guild_id)
        except ValueError:
            await interaction.response.send_message("Invalid guild ID provided. Please ensure it's a valid number.")
            return
    
        # Retrieve the guild's membership details from the database
        membership_details = await retrieve_guild_membership(guild_id_int)
        
        if membership_details:
            # Convert the expiry timestamp to a human-readable date and time
            expiry_date = datetime.utcfromtimestamp(membership_details["expiry_date"]).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            # Create a message embed to display the guild's membership details
            embed = nextcord.Embed(title="**Guild Membership Details**", description="\n\n", color=0x00ff00)
            embed.add_field(name="**Guild Name**", value=f"*{membership_details['guild_name']}*\n\u200B", inline=False)
            embed.add_field(name="**Guild ID**", value=f"*{membership_details['guild_id']}*\n\u200B", inline=False)
            embed.add_field(name="**Membership Type**", value=f"*{membership_details['membership_type']}*\n\u200B", inline=False)
            embed.add_field(name="**Expiration Date**", value=f"*{expiry_date}*\n\u200B", inline=False)
            embed.add_field(name="**Subscription Active**", value=f"*{membership_details['subscription_active']}*\n\u200B", inline=False)
            
            # Send the embed message
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No membership details found for the provided guild ID.")

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
