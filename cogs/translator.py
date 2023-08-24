import nextcord
from nextcord.ext import commands, tasks
import asyncio
import openai
from src.lang_processing import should_translate
from database.database_manager import (
    insert_translation,
    delete_old_translations
)
from src.discord_ui import (
    TranslationButton,
    TranslationView
)
from datetime import datetime

class TranslationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translations = {}  # Dictionary to store translations (no longer needed but kept for reference)
        self.cleanup_task = self.clean_translations.start()
        print("AppCommands cog initialized") 
      
    @commands.Cog.listener()
    async def on_ready(self):
        print("Translator ready")
  
    @tasks.loop(hours=12)
    async def clean_translations(self):
        await delete_old_translations()

    async def disable_button(self, message_id: int, channel_id: int):
        print(f"[{datetime.now()}] Started 30 sec wait for message ID: {message_id}")  # Debug with timestamp
        await asyncio.sleep(30)  # 30 sec button lifespan
    
        channel = self.bot.get_channel(channel_id)
        if not channel:
            print(f"Failed to fetch channel with ID: {channel_id}")
            return
    
        message = await channel.fetch_message(message_id)
        if not message:
            print(f"Failed to fetch message with ID: {message_id}")
            return
    
        await message.delete()  # This line deletes the message containing the button
        print(f"[{datetime.now()}] Deleted message with ID: {message_id}")  #deletion confirmed

    @commands.Cog.listener()
    async def on_message(self, message):
        # Make sure the author of the message is not a bot
        if not message.author.bot:
            # Display a non-functional button without the label argument
            dummy_view = TranslationView(self, message_id=message.id)
            dummy_message = await message.channel.send("", view=dummy_view)
        
            # Check if the message should be translated
            if not await should_translate(message.content):
                await dummy_message.delete()  # delete the dummy button/message if not translating
                return
    
            system_prompt = (
                "Your singular purpose is to translate any non-English language you receive into perfect English, while ensuring you maintain and accurately represent any cultural nuances and slang expressed in the original text."
            )
    
            chat_message = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Translate the following to English: '{message.content}'"}
            ]
    
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=chat_message,
                temperature=0.2,
                max_tokens=500,
                frequency_penalty=0.0
            )
            translation = response['choices'][0]['message']['content'].strip()
            await insert_translation(str(message.id), translation, str(message.id))
            
            # Replace the dummy button with a functional TranslationButton
            dummy_view.clear_items()
            translation_button = TranslationButton(message_id=message.id, label="View Translation", style=nextcord.ButtonStyle.grey)
            dummy_view.add_item(translation_button)
            await dummy_message.edit(view=dummy_view)
    
            # This line is where you create the task to disable the button after 30 seconds
            self.bot.loop.create_task(self.disable_button(dummy_message.id, message.channel.id))


def cog_unload(self):
        self.cleanup_task.cancel()

def setup(bot):
    bot.add_cog(TranslationCog(bot))
    print("Translation cog loaded")