import os, random
from datetime import datetime

import discord
from discord.ext import commands, tasks

from myconstants import greetings, mynames

import db_manager

# --------------------------------------------------------------------------- #

# Tests:
#from cogs.schedule import test
#test()

# --------------------------------------------------------------------------- #
# Bot Init

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=',', intents=intents)
bot.remove_command('help')

# --------------------------------------------------------------------------- #
# Cog Loading

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

bot.load_extension("cogs.roles")
bot.load_extension("cogs.schedule")

# --------------------------------------------------------------------------- #
# Misc Setup

@bot.command()
async def help(ctx):
    help_str = "Commands:\n\t"
    help_str += ",notify <true|false>\n\t\t// activates or deactivates notifications\n\t"
    help_str += ",ping\t\t\n\t\t// pong\n\t"
    help_str += ",gamejam\n\t\t// lists the 8 most popular game jams from itch.io\n\t"
    help_str += ",gamejam more\n\t\t// 16 most popular game jams from itch.io\n\t"
    help_str += ",gamejam soon\n\t\t// lists 4 most popular game jams from itch.io running this week\n\t"
    help_str += ",join jam_name\n\t\t// gives notifications 7 days before, 24 hours before, and 1 hour before the jam starts. (Not yet completed)\n\n"
    help_str += "Interaction:\n\tTry saying hi to CubeBot"
    await ctx.send("```{}```".format(help_str))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="conway's game of life"))
    every_minute_loop.start()
    print("CubeBot is ready")

@bot.event
async def on_member_join(member):
    # TODO: give basic role?
    pass

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    val = await bot.process_commands(message)
    print("did process cmd: {}".format(val))

    cleaned_msg = message.content.replace("!", "").replace("?", "").lower().strip()
    ends_with_myname = cleaned_msg.endswith(mynames[0].lower()) or cleaned_msg.endswith(mynames[1].lower())
    if ends_with_myname and len(cleaned_msg) > 9 and cleaned_msg[:-8].strip() in greetings:
        end_char = "!" if random.randint(0, 1) == 1 else ""
        await message.channel.send("{} {}{}".format(random.choice(greetings), message.author.mention, end_char))
    elif "linux" in cleaned_msg and not "gnu linux" in cleaned_msg:
        await message.channel.send("you mean GNU linux, right?")    

# --------------------------------------------------------------------------- #
# New Users

@bot.event
async def on_member_join(member):
    guild = bot.get_guild(int(os.environ["MAIN_SERVER_ID"]))
    channel = discord.utils.get(guild.channels, name="bot-spam", type="ChannelType.text")
    await channel.send("Welcome {}!".format(member.mention))
    #channel.send("To get started, please pick a colour by reacting to this message.")
    await channel.send("We have informal meetings every second monday at **8:00pm** where we talk about anything and everything somewhat related to game development, then people give short demos of what they've been working on recently. If you've ever worked on a game or have something cool to show off, we'd love it if you'd like to demo it!".format(member.mention))
    await channel.send("Our next meeting is on June 27th.")
    
# --------------------------------------------------------------------------- #
# Notifications

# We use this variable in case we accidentally miss 5:30 by 1 minute.
done_friday_update = False

@tasks.loop(minutes=1)
async def every_minute_loop():
    global done_friday_update

    now = datetime.now()
    
    #if now.weekday() == 4 and now.hour == 12+5 and now.minute >= 30 and not done_friday_update:
    if now.hour == 12+11 and now.minute >= 30 and not done_friday_update:
        guild = bot.get_guild(int(os.environ["MAIN_SERVER_ID"]))
        channel = discord.utils.get(guild.channels, name="bot-test")
        await channel.send("Weekly update that we did it")
        print("did it")
        done_friday_update = True

    if now.hour == 0 and done_friday_update:
    #if now.weekday() == 4 and now.hour == 6 and done_friday_update:
        done_friday_update = False

# --------------------------------------------------------------------------- #
# Managing Events

@commands.has_role('Executive')
@bot.command()
async def reset_events(ctx):
    db_manager.reset_events_table()
    await ctx.send("Events have been reset")

@commands.has_role('Executive')
@bot.command()
async def add_event(ctx, unique_name, date, desc):
    try:
        parts = date.split("-")
        parts = list(map(int, parts))
        date_ = datetime(year=parts[0], month=parts[1], day=parts[2], hour=parts[3], minute=parts[4])
        db_manager.add_event(unique_name, date_, desc)
        await ctx.send("Successfully added event `{}`".format(unique_name))
    except:
        await ctx.send("Syntax error: date must be 5 parts split by '-' characters. Ex: `yyyy-mm-dd-hh-mm` => `2021-05-25-23-46`")
        

@commands.has_role('Executive')
@bot.command()
async def edit_event(ctx, unique_name, desc):
    await ctx.send("TODO: implement this")

@bot.command()
async def events(ctx):
    await ctx.send("TODO: implement this")

# --------------------------------------------------------------------------- #
# Website Output?

pass

# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    print("about to run bot")
    bot.run(os.environ['TOKEN']) # this token is set in the heroku environment
else:
    print("ran the file in lint mode, exiting gracefully.")