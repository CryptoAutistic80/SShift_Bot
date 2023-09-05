import nextcord
import openai
import logging
from nextcord.ext import commands
from database.database_manager import retrieve_translation_by_original_message_id
from main import TRANSLATOR_MODEL
from src.utils import MEMBER_GUILDS
import asyncio


class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logging.info("CommandsCog initialized")
        print("CommandsCog cog initialized")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Commands Loaded")
      
    ################
    # ADMIN COMMANDS
    ################
          
    @commands.command(name="setup", help="Set up the bot's permissions for a specific channel")
    @commands.has_guild_permissions(administrator=True)  # Ensure the user has admin permissions
    async def setup_command(self, ctx):
        # Prompt the user for the bot's nickname
        await ctx.send("Please name me:")
        
        def check_nickname(message):
            # Ensure the response is from the command invoker and in the same channel
            return message.author == ctx.author and message.channel == ctx.channel
    
        try:
            # Wait for the user's response for the nickname
            nickname_response = await self.bot.wait_for('message', check=check_nickname, timeout=60)  # Wait for 60 seconds
            
            # Set the bot's nickname
            bot_member = ctx.guild.get_member(self.bot.user.id)
            await bot_member.edit(nick=nickname_response.content)
            await ctx.send(f"Bot's nickname set to {nickname_response.content}.")
            
            # Prompt the user for the channel
            await ctx.send("Please provide the channel ID or mention the channel using #channel-name thatvwould would like me to operate in:")
            
            def check_channel(message):
                return message.author == ctx.author and message.channel == ctx.channel
        
            # Wait for the user's response for the channel
            response = await self.bot.wait_for('message', check=check_channel, timeout=60)  # Wait for 60 seconds
            
            # Extract channel ID from the response
            if response.content.startswith("<#") and response.content.endswith(">"):
                channel_id = int(response.content[2:-1])
            else:
                channel_id = int(response.content)
                
            specified_channel = ctx.guild.get_channel(channel_id)
            if not specified_channel:
                await ctx.send("Invalid channel provided. Please ensure you provide a valid channel ID or mention.")
                return
    
            # Create the "Translator" role with the desired permissions
            permissions = nextcord.Permissions(
                read_messages=True,
                read_message_history=True,
                send_messages=True,
                manage_messages=True,
                add_reactions=True,
                use_slash_commands=True
            )
            translator_role = await ctx.guild.create_role(name="Translator", permissions=permissions, color=nextcord.Color.blue())
            await ctx.send("'Translator' role created.")
            
            # Assign the "Translator" role to the bot
            await bot_member.add_roles(translator_role)
            await ctx.send("'Translator' role assigned to the bot.")
                
            # Iterate over all channels and set the bot's permissions
            for channel in ctx.guild.channels:
                if channel == specified_channel:
                    continue  # Skip the specified channel
                overwrites = channel.overwrites_for(ctx.guild.me) or nextcord.PermissionOverwrite()
                overwrites.read_messages = False
                await channel.set_permissions(ctx.guild.me, overwrite=overwrites)
                
            # Define the permissions for the bot in the user-specified channel
            channel_permissions = nextcord.PermissionOverwrite(
                read_messages=True,
                read_message_history=True,
                send_messages=True,
                manage_messages=True,
                add_reactions=True,
                use_slash_commands=True
            )
            # Apply the permissions to the specified channel
            await specified_channel.set_permissions(ctx.guild.me, overwrite=channel_permissions)
                
            await ctx.send(f"Bot's permissions have been set up for {specified_channel.mention}. Now remove the 'Administrator' permission from the bot's primary role in Discord settings to complete the setup process.")
            
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please use the command again and provide the information.")
        except Exception as e:
            logging.error(f"Error executing !setup command: {e}")
            await ctx.send("An unexpected error occurred. Please try again.")

  
    #################
    # USER COMMANDS
    #################

    @commands.command(name="fetch", help="Fetch the translation for a replied message")
    async def fetch_command(self, ctx):
        """Fetch the translation for a replied message using traditional command"""
        try:
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
        except Exception as e:
            logging.error(f"Error executing !fetch command: {e}")
            await ctx.send("An error occurred. Please try again later.")


    @commands.command(name="reply", help="Translate your reply to the language of the original message", guild_ids=MEMBER_GUILDS.get())
    async def reply_command(self, ctx, *, user_reply: str):
        try:
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
                    model=TRANSLATOR_MODEL,
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
        except Exception as e:
            logging.error(f"Error executing !reply command: {e}")
            await ctx.send("An error occurred. Please try again later.")

def setup(bot):
    bot.add_cog(CommandsCog(bot))
    print("Command Cog loaded")
    logging.info("CommandsCog has been loaded")

