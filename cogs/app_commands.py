import nextcord
import openai
from nextcord.ext import commands
from src.lang_processing import is_english, preprocess_message, should_translate
from main import MEMBER_GUILDS, TRANSLATOR_MODEL
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

    #################
    # ADMIN COMMANDS
    #################

    @nextcord.slash_command(name="admin", description="Admin functions.", guild_ids=MEMBER_GUILDS)
    async def admin(self, interaction: nextcord.Interaction):
        try:
            logging.info(f"/admin command invoked by {interaction.user.name} ({interaction.user.id})")
            await interaction.response.send_message("Coming Soon")
        except Exception as e:
            logging.error(f"Error executing /admin command: {e}")

    #################
    # USER COMMANDS
    #################

    @nextcord.slash_command(name="reply", description="Reply to a user's last message.", guild_ids=MEMBER_GUILDS)
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
