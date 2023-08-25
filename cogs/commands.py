import nextcord
import openai
import logging
from nextcord.ext import commands
from database.database_manager import retrieve_translation_by_original_message_id
import asyncio


class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logging.info("CommandsCog initialized")
        print("CommandsCog cog initialized")

    @commands.Cog.listener()
    async def on_ready(self):
      print("Commands Loaded")
    

    @commands.command(name="fetch", help="Fetch the translation for a replied message")
    async def fetch_command(self, ctx):
        """Fetch the translation for a replied message using traditional command"""
        logging.info(f"!fetch command invoked by {ctx.author.name} ({ctx.author.id})")
        
        # Check if the context is in reply to an existing message
        if ctx.message.reference:
            original_message_id = ctx.message.reference.message_id
            
            # Fetch the translation from the database
            translation = await retrieve_translation_by_original_message_id(ctx.guild.id, original_message_id)
            
            # If a translation exists, send it
            if translation:
                await ctx.send(translation)
            else:
                await ctx.send(f"No translation found for message ID {original_message_id}")
        else:
            await ctx.send("Please reply to a message to fetch its translation.")


  
    @commands.command(name="reply", help="Translate your reply to the language of the original message")
    async def reply_command(self, ctx, *, user_reply: str):
        logging.info(f"!reply command invoked by {ctx.author.name} ({ctx.author.id})")
        
        # Check if the context is in reply to an existing message
        if ctx.message.reference:
            original_message_id = ctx.message.reference.message_id
            original_message = await ctx.channel.fetch_message(original_message_id)
            original_content = original_message.content
    
            # Construct the prompt for OpenAI
            system_prompt = (
                "Your purpose is to translate replies to match the language of the original message, while ensuring you maintain any cultural nuances and slang."
            )
            chat_message = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Original message: '{original_content}'. Translate the following reply to the same language: '{user_reply}'."}
            ]
    
            # Use OpenAI API to get the translation
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=chat_message,
                temperature=0.2,
                max_tokens=500,
                frequency_penalty=0.0
            )
            translation = response['choices'][0]['message']['content'].strip()
    
            # Delete the user's original !reply message
            await ctx.message.delete()
    
            # Bot replies to the original message with the formatted translation
            formatted_translation = f"{ctx.author.mention} replied: {translation}"
            await original_message.reply(formatted_translation)
    
        else:
            logging.info("The !reply command was not used in reply to a message.")
            await ctx.send("Please use the !reply command in response to an existing message.")

          

def setup(bot):
    bot.add_cog(CommandsCog(bot))
    print("Command Cog loaded")
    logging.info("CommandsCog has been loaded")
