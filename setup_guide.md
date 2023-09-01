# Bot Setup Guide

This guide will walk you through the process of setting up the bot's permissions for a specific channel using the `setup` command.

**Note:** Before proceeding, ensure that you have the `Administrator` permissions in the server.

1. Open the desired channel in your server where you want the bot to operate.

2. Type the following command in any channel that the bot can see: !setup; This will initiate the setup process.

3. The bot will prompt you to provide the channel where you want to set up its permissions. You can either mention the channel using the `#channel-name` format or provide the channel ID. Reply to the bot's prompt with the necessary information.

4. The bot will then perform the following steps:

a. Create a role named "Translator" with the necessary permissions to operate in the specified channel.

b. Assign the "Translator" role to the bot.

c. Restrict the bot's permissions in all other channels to prevent interference.

d. Set up specific permissions for the bot in the user-specified channel.

5. After the setup process is complete, the bot will send a confirmation message indicating that its permissions have been configured for the specified channel.

6. **Important:** To finalize the setup, you need to manually remove the `Administrator` permission from the bot's primary role in your Discord server settings. This step ensures that the bot operates securely and correctly without unnecessary privileges.

**Note:** If you encounter any issues during the setup process, you can retry the command or contact the SShift DAO for assistance.

Remember that the bot will only operate in the channel you've specified, and its permissions in other channels will be restricted as per the setup process.

For any further questions or assistance, feel free to reach out to SShift DAO.

That's it! Your bot is now set up and ready to operate in the specified channel.

