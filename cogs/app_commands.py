import nextcord
import openai
from nextcord.ext import commands
from src.lang_processing import is_english, preprocess_message, should_translate
import logging

class AppCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("AppCommands cog initialized")  # Add this line

    @commands.Cog.listener()
    async def on_ready(self):
        print("app commands live")


    #################
    # ADMIN COMMANDS
    #################

    @nextcord.slash_command(name="admin", description="Admin functions.", guild_ids=[1098355558022656091, 1099667794016092210, 1124052286155534437])
    async def admin(self, interaction: nextcord.Interaction):
        """Admin functions coming soon."""
        logging.info(f"/admin command invoked by {interaction.user.name} ({interaction.user.id})")
        await interaction.response.send_message("Coming Soon")


    #################
    # USER COMMANDS
    #################

      
    @nextcord.slash_command(name="reply", description="Reply to a user's last message.", guild_ids=[1098355558022656091, 1099667794016092210])
    async def reply(self, interaction: nextcord.Interaction, user: nextcord.Member, text: str):
        logging.info("Received /reply command.")
        
        # Defer the interaction to let Discord know the bot will respond shortly
        await interaction.response.defer()
        
        # Send the "Processing" message and store it in a variable
        processing_msg = await interaction.followup.send("Processing your translation request...")
        
        # Fetch the last 50 messages in the channel
        messages = await interaction.channel.history(limit=50).flatten()
        
        # Find the last non-English message from the selected user that should be translated
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
        
        # Construct the prompt for OpenAI
        system_prompt = (
            "Translate the reply to match the language and style of the original message."
        )
        chat_message = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Original message: '{original_content}'. Reply: '{text}'."}
        ]
        
        # Use OpenAI API to get the translation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_message,
            temperature=0.2,
            max_tokens=500,
            frequency_penalty=0.0
        )
        translation = response['choices'][0]['message']['content'].strip()
        
        # Send the translated reply
        response_message = f"{interaction.user.mention} replied:\n\n**Original:** {text}\n\n**Translation:** {translation}"
        await user_message.reply(response_message)
        
        # Delete the "Processing" message
        await processing_msg.delete()


def setup(bot):
    bot.add_cog(AppCommands(bot))
    print("AppCommands cog loaded")


