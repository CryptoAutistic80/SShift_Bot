import nextcord
from nextcord.ext import commands, tasks
import openai
import os
import re
import langid
from config import TRANSLATE_CONFIG
from database.database_manager import insert_translation, retrieve_translation, delete_old_translations

# Initialize the OpenAI API
openai.api_key = os.environ['Key_OpenAI']

def is_english(text):
    lang, _ = langid.classify(text)
    return lang == 'en'

def preprocess_message(text):
    # Remove mentions
    cleaned_text = re.sub(r'@\w+', '', text)
    return cleaned_text.strip()

def should_translate(text):
    cleaned_text = preprocess_message(text)

    # If the cleaned message is empty, don't translate
    if not cleaned_text:
        return False

    # Check for non-Latin scripts
    non_latin_patterns = [
        r'[\u0600-\u06FF]',  # Arabic
        r'[\u0980-\u09FF]',  # Bengali
        r'[\u4E00-\u9FFF\U00020000-\U0002A6DF]',  # Chinese
        r'[\u0400-\u04FF]',  # Cyrillic
        r'[\u0900-\u097F]',  # Devanagari
        r'[\u0370-\u03FF]',  # Greek
        r'[\u0A80-\u0AFF]',  # Gujarati
        r'[\u0A00-\u0A7F]',  # Gurmukhi
        r'[\u0590-\u05FF]',  # Hebrew
        r'[\u3040-\u30ff\u3400-\u4DBF]',  # Japanese
        r'[\u0C80-\u0CFF]',  # Kannada
        r'[\uAC00-\uD7AF]',  # Korean
        r'[\u0D00-\u0D7F]',  # Malayalam
        r'[\u0B00-\u0B7F]',  # Oriya (Odia)
        r'[\u0D80-\u0DFF]',  # Sinhala
        r'[\u0B80-\u0BFF]',  # Tamil
        r'[\u0C00-\u0C7F]',  # Telugu
        r'[\u0E00-\u0E7F]',  # Thai
        r'[\u0F00-\u0FFF]'   # Tibetan
    ]
    for pattern in non_latin_patterns:
        if re.search(pattern, cleaned_text):
            return True

    # Check for minimum number of words on cleaned text
    if len(cleaned_text.split()) < 2:
        return False
    
    # Check for URLs on cleaned text
    url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    if re.search(url_regex, cleaned_text):
        return False

    # Return False if the message is in English
    return not is_english(cleaned_text)

class TranslationButton(nextcord.ui.Button):
    def __init__(self, message_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_id = message_id

    async def callback(self, interaction: nextcord.Interaction):
        translation = await retrieve_translation(str(self.message_id))
        if not translation:
            translation = "Translation not found."
        # Send the translation as an ephemeral message
        await interaction.response.send_message(translation, ephemeral=True)

class TranslationView(nextcord.ui.View):
    def __init__(self, cog, message_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cog = cog
        self.add_item(TranslationButton(message_id, label="View Translation", style=nextcord.ButtonStyle.grey))

class TranslationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translations = {}  # Dictionary to store translations (no longer needed but kept for reference)
        self.cleanup_task = self.clean_translations.start()

    @tasks.loop(hours=12)
    async def clean_translations(self):
        """Cleanup task to remove translations older than 12 hours."""
        await delete_old_translations()

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.process_commands(message)
        guild_id = message.guild.id
        channel_id = message.channel.id
            
        # Check if the message's guild and channel IDs match the TRANSLATE_CONFIG
        if guild_id in TRANSLATE_CONFIG and channel_id in TRANSLATE_CONFIG[guild_id]['channels'] and not message.author.bot:
            if should_translate(message.content):
                chat_message = [{"role": "user", "content": f"Translate the following to English: '{message.content}'"}]
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=chat_message,
                    temperature=0.1,
                    max_tokens=500,
                    frequency_penalty=0.0
                )
                translation = response['choices'][0]['message']['content'].strip()
                await insert_translation(str(message.id), translation)
                
                # Send an empty message with just the 'Translation' button below the original message
                view = TranslationView(self, message_id=message.id, timeout=None)
                await message.channel.send("", view=view)

    def cog_unload(self):
        self.cleanup_task.cancel()

def setup(bot):
    bot.add_cog(TranslationCog(bot))
    print("Translation cog loaded")