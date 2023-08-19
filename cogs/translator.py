import nextcord
from nextcord.ext import commands, tasks
import asyncio
import openai
import os
import re
import langid
from config import TRANSLATE_CONFIG
from database.database_manager import insert_translation, retrieve_translation, delete_old_translations
from datetime import datetime

# Initialize the OpenAI API
openai.api_key = os.environ['Key_OpenAI']

def is_english(text):
    lang, _ = langid.classify(text)
    return lang == 'en'

def preprocess_message(text):
    # Remove mentions
    cleaned_text = re.sub(r'@\\w+', '', text)
    return cleaned_text.strip()

def should_translate(text):
    print(f"Debug: Text being passed to should_translate: {text}")
    cleaned_text = preprocess_message(text)

    if not cleaned_text:
        print("Debug: Message is empty.")
        return False

    if is_english(cleaned_text):
        print("Debug: Message is in English.")
        return False

    # Check for non-Latin scripts
    non_latin_patterns = [
        r'[\u0600-ۿ]',  # Arabic
        r'[ঀ-\u09ff]',  # Bengali
        r'[一-\u9fff𠀀-\U0002a6df]',  # Chinese
        r'[Ѐ-ӿ]',  # Cyrillic
        r'[ऀ-ॿ]',  # Devanagari
        r'[Ͱ-Ͽ]',  # Greek
        r'[\u0a80-૿]',  # Gujarati
        r'[\u0a00-\u0a7f]',  # Gurmukhi
        r'[\u0590-\u05ff]',  # Hebrew
        r'[\u3040-ヿ㐀-\u4dbf]',  # Japanese
        r'[ಀ-\u0cff]',  # Kannada
        r'[가-\ud7af]',  # Korean
        r'[ഀ-ൿ]',  # Malayalam
        r'[\u0b00-\u0b7f]',  # Oriya (Odia)
        r'[\u0d80-\u0dff]',  # Sinhala
        r'[\u0b80-\u0bff]',  # Tamil
        r'[ఀ-౿]',  # Telugu
        r'[\u0e00-\u0e7f]',  # Thai
        r'[ༀ-\u0fff]'   # Tibetan
    ]
    for pattern in non_latin_patterns:
        if re.search(pattern, cleaned_text):
            print("Debug: Message contains non-Latin scripts.")
            return True

    if len(cleaned_text.split()) < 5:
        print("Debug: Message has less than 5 words.")
        return False
    
    url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\\\(\\\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    if re.search(url_regex, cleaned_text):
        print("Debug: Message contains a URL.")
        return False

    print("Debug: Message passed all checks and will be translated.")
    return True

class TranslationButton(nextcord.ui.Button):
    def __init__(self, message_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_id = message_id

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        translation = await retrieve_translation(str(self.message_id))
        if not translation:
            translation = "Translation not found."
        await interaction.followup.send(translation, ephemeral=True)

class TranslationView(nextcord.ui.View):
    def __init__(self, cog, message_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cog = cog
        self.add_item(TranslationButton(message_id, label="Translating...", style=nextcord.ButtonStyle.grey, disabled=True))

class TranslationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translations = {}  # Dictionary to store translations (no longer needed but kept for reference)
        self.cleanup_task = self.clean_translations.start()

    @tasks.loop(hours=12)
    async def clean_translations(self):
        await delete_old_translations()

    async def disable_button(self, message_id: int, channel_id: int):
        print(f"[{datetime.now()}] Started 1-minute wait for message ID: {message_id}")  # Debug with timestamp
        await asyncio.sleep(60)  # 1 minute for testing
    
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
        await self.bot.process_commands(message)
        guild_id = message.guild.id
        channel_id = message.channel.id
            
        # Check if the message's guild and channel IDs match the TRANSLATE_CONFIG
        if guild_id in TRANSLATE_CONFIG and channel_id in TRANSLATE_CONFIG[guild_id]['channels'] and not message.author.bot:
            if should_translate(message.content):
                # Display a non-functional button with label "Translating..."
                dummy_view = TranslationView(self, message_id=message.id, timeout=None)
                dummy_message = await message.channel.send("", view=dummy_view)

                system_prompt = (
                    "Your singular purpose is to translate any non-English language you receive into perfect English, "
                    "while ensuring you maintain and accurately represent any cultural nuances and slang expressed in the original text."
                )

                chat_message = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Translate the following to English: '{message.content}'"}
                ]

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=chat_message,
                    temperature=0.2,
                    max_tokens=500,
                    frequency_penalty=0.0
                )
                translation = response['choices'][0]['message']['content'].strip()
                await insert_translation(str(message.id), translation)
                
                # Edit the dummy button's label to "View Translation" and activate its functionality
                dummy_view.clear_items()
                dummy_view.add_item(TranslationButton(message_id=message.id, label="View Translation", style=nextcord.ButtonStyle.grey))
                await dummy_message.edit(view=dummy_view)

                # This line is where you create the task to disable the button after 1 minute
                self.bot.loop.create_task(self.disable_button(dummy_message.id, message.channel.id))

    def cog_unload(self):
        self.cleanup_task.cancel()

def setup(bot):
    bot.add_cog(TranslationCog(bot))
    print("Translation cog loaded")
