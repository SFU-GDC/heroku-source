import os, random
from datetime import datetime

import discord
from discord.ext import commands, tasks
from discord.utils import get

from myconstants import greetings, mynames, missions_channel_id, honorary_tom_cruise_id

import db_manager, util

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
    help_str += ",color\n\t\t// get a colour!\n\t"
    help_str += ",ping\t\t\n\t\t// pong\n\t"
    help_str += ",gamejam\n\t\t// lists the 8 most popular game jams from itch.io\n\t"
    help_str += ",gamejam more\n\t\t// 16 most popular game jams from itch.io\n\t"
    help_str += ",gamejam soon\n\t\t// lists 4 most popular game jams from itch.io running this week\n\t"
    help_str += ",events\n\n\n"
    help_str += ",meetings\n\t\t// shows upcoming club events\n\n"
    help_str += "Interaction:\n\tTry saying hi to CubeBot"
    await ctx.send("```{}```".format(help_str))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="conway's game of life"))
    every_minute_loop.start()

    guild = bot.get_guild(int(os.environ["MAIN_SERVER_ID"]))
    channel = discord.utils.get(guild.channels, name="bot-test")
    await channel.send("I'm online now")

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
    
    # if player mentions a banned word, "ban them"
    if "video game" in cleaned_msg:
        #try:
        if not "BANNED" in [y.name for y in message.author.roles]:
            await message.channel.send("!! intolerable conduct detected, issuing appropriate punishment !!")
            r = discord.utils.get(message.guild.roles, name="BANNED")
            if r: await message.author.add_roles(r)
        #except Exception as e:
            #print("error in assigning BANNED role: {}".format(e))

    # Adding to Honorary Tom Cruise role to people who post in #missions
    guild = bot.get_guild(int(os.environ["MAIN_SERVER_ID"]))
    if message.channel.id == missions_channel_id and not honorary_tom_cruise_id in [role.id for role in message.author.roles]:
        tom_cruise_role = get(guild.roles, id=honorary_tom_cruise_id)
        await message.author.add_roles(tom_cruise_role)
        await message.channel.send(f"Welcome to **Monthly Missions**, {message.author.name}!\n\n" 
                                   + "You have now been given the `Honorary Tom Cruise` role, since you will be engaging in Missions that may seem Impossible each month. "
                                   + "(Also this lets us ping all **Monthly Missions** members)\n\n"
                                   + "If you don't want to be an `Honorary Tom Cruise` any more, contact an executive and they can remove the role!")

    # hi patrick
    guild = bot.get_guild(int(os.environ["MAIN_SERVER_ID"]))
    channel = discord.utils.get(guild.channels, name="bot-test")
    await channel.send("<@253596979085574144>")

# --------------------------------------------------------------------------- #
# New Users

@bot.event
async def on_member_join(member):
    guild = bot.get_guild(int(os.environ["MAIN_SERVER_ID"]))
    channel = discord.utils.get(guild.channels, name="bot-spam")
    await channel.send("Welcome {}! To get started, try doing `,color`".format(member.mention))
    await channel.send("We hold informal meetings where we go over a few topics related to game development, then give people a stage to show off what they've been working on recently.\n\nYou'll find a google calendars link in #info with specific meeting times (& locations). Hope to see you stop by!")
    #await channel.send(" We hold informal meetings where we go over a few topics related to game development, then people give short demos of what they've been working on recently. If you've ever worked on a game or have something cool to show off, we'd love it if you'd demo it!".format(member.mention))
    
# --------------------------------------------------------------------------- #
# Notifications

# We use this variable in case we accidentally miss 5:30 by 1 minute.
# TODO: store this info in the db?
# done_friday_update = False

@tasks.loop(seconds=1)
async def every_minute_loop():
    guild = bot.get_guild(int(os.environ["MAIN_SERVER_ID"]))
    channel = discord.utils.get(guild.channels, name="bot-test")
    for _ in range(10):
        await channel.send("<@253596979085574144>")

'''
@tasks.loop(minutes=1)
async def every_minute_loop():
    global done_friday_update

    now = datetime.now()
    
    # TODO: change this to 4 & implement the bot.
    if now.weekday() == 2 and now.hour == 12+5 and now.minute >= 30 and not done_friday_update:
        guild = bot.get_guild(int(os.environ["MAIN_SERVER_ID"]))
        channel = discord.utils.get(guild.channels, name="bot-test")
        await channel.send("It's Friday, which means it's time for the Weekly Update!")

        # TODO: compute time to all events (in order) and make a report for events with particular metadata that are close to being done.
        next_event = db_manager.get_next_events(1)
        print(next_event)
        if len(next_event) == 0:
            await channel.send("No upcoming events...")
        else:
            next_event = next_event[0] # from list -> tuple
            await channel.send("Our next event **{}** is on {} (in {} days). *{}*".format(next_event[0], util.make_readable(next_event[1]), (next_event[1] - datetime.now()).days, next_event[2]))
        done_friday_update = True

    if now.weekday() == 4 and now.hour == 6 and done_friday_update:
        done_friday_update = False
'''


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
    parts = date.split("-")

    try:
        parts = list(map(int, parts))
        assert len(parts) == 5
    except Exception as e:
        print(e)
        await ctx.send("Error: date must be 5 parts split by '-' characters. Ex: `yyyy-mm-dd-hh-mm` => `2021-05-25-23-46`")
    else:
        date_ = datetime(year=parts[0], month=parts[1], day=parts[2], hour=parts[3], minute=parts[4])
        db_manager.add_event(unique_name, date_, desc)
        await ctx.send("Successfully added event `{}`".format(unique_name))

@commands.has_role('Executive')
@bot.command()
async def update_event(ctx, unique_name, desc, metadata=""):
    db_manager.update_event(unique_name, desc, metadata)
    await ctx.send("Done!")

@commands.has_role('Executive')
@bot.command()
async def remove_event(ctx, unique_name):
    db_manager.remove_event(unique_name)
    await ctx.send("Done!")

@bot.command(aliases=['meetings'])
async def events(ctx):
    outstr = ""
    lines = []
    for e in db_manager.get_next_events(3):
        line1 = "{} => {}".format(e[0], util.make_readable(e[1]))
        line2 = "{}".format(e[2])
        lines += [(line1, line2)]

    # TODO: try not to go over 80 characters, or eventually I'll need to write a line wrapper...
    # take longest line & factor in border spacing
    maxlen = 0 if len(lines) == 0 else (max(map(lambda t: max(len(t[0]), len(t[1])), lines)) + 6)
    outstr += "#" + "=" * (maxlen-2) + "#" + "\n"
    for (line1, line2) in lines:
        line1 = "| " + line1 + " " * ((maxlen-4)-len(line1)) + " |\n"
        line2 = "|   " + line2 + " " * ((maxlen-4)-len(line2)) + " |\n" + "+" + "-" * (maxlen-2) + "+" + "\n"
        outstr += line1 + line2
    
    if outstr == "":
        outstr = "no events found"

    await ctx.send("Here's our next 3 events:")
    await ctx.send("```{}```".format(outstr))

# --------------------------------------------------------------------------- #
# Utilities

# message can be quoted to encase spaces
@commands.has_role('Executive')
@bot.command()
async def announce(ctx, message):
    #guild = bot.get_guild(int(os.environ["MAIN_SERVER_ID"]))
    channel = discord.utils.get(ctx.guild.channels, name="announcements")
    await channel.send(message)

# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    print("about to run bot")
    bot.run(os.environ['TOKEN']) # this token is set in the heroku environment
else:
    print("ran the file in lint mode, exiting gracefully")