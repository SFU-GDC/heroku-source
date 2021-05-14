import os, random

import discord
from discord.ext import commands, tasks

from myconstants import greetings

# --------------------------------------------------------------------------- #
# Bot Init

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=',', intents=intents)
#bot.remove_command('help')

# --------------------------------------------------------------------------- #
# Cog Loading

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

# --------------------------------------------------------------------------- #
# Misc Setup

@bot.command()
async def setallmembers(ctx):
    pass # todo: set all members to the "member" role.

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="conway's game of life"))
    print("CubeBot is Ready")

@bot.event
async def on_member_join(member):
    # TODO: give basic role
    pass

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    cleaned_msg = message.content.replace("!", "").replace("?", "").lower()
    if cleaned_msg.endswith("cubebot") and len(cleaned_msg) > 9 and cleaned_msg[:-8] in greetings:
        await message.channel.send(random.choice(greetings) + str(message.author))

# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    print("about to run bot")
    bot.run(os.environ['TOKEN']) # this token is set in the heroku environment
else:
    print("ran the file in lint mode, exiting gracefully.")