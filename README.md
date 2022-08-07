# 2gb-pterodactyl-load-bot
Discord bot that shows current load and resource usage of a specified Pterodactyl server.

# Installation
Clone the repo.

`git clone https://github.com/rathmerdominik/pterodactyl-load-bot.git`

Install dependencies

`pip install -r requirements.txt`

Then you have to create a .env and config.yaml file from the existing dist files.

`cp config.dist.yaml config.yaml`

`cp .dist.env .env`

After that you have to define the values inside the .env file.

`DISCORD_TOKEN` has to be a bot token. [Here](https://www.writebots.com/discord-bot-token/) is a guide to get one.

`DISCORD_CHANNEL_ID` has to be the ID of a Guild channel. [Here](https://www.youtube.com/watch?v=NLWtSHWKbAI) is a guide to get the ID from a specific channel.

`PTERO_API_KEY` has to be a Pterodactyl User API Key. To get one you can visit this site https://example.com/account/api where example.com is the Domain for your Pterodactyl installation.

`PTERO_SERVER` has to be the Domain of your panel

You can start the bot afterwards with

`python3 ptero-load-bot.py`
 