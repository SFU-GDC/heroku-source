import os, random
from datetime import datetime

import discord
from discord.ext import commands, tasks
from discord.utils import get

from myconstants import greetings, mynames, missions_channel_id, honorary_tom_cruise_id

import util

# --------------------------------------------------------------------------- #

# Tests:
#from cogs.schedule import test
#test()

# --------------------------------------------------------------------------- #
# Bot Init

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=',', intents=intents)
bot.remove_command('help')

# --------------------------------------------------------------------------- #
# Cog Loading

@bot.command()
async def load(ctx, extension):
    await bot.load_extension(f'cogs.{extension}')

@bot.command()
async def unload(ctx, extension):
    await bot.unload_extension(f'cogs.{extension}')

# --------------------------------------------------------------------------- #
# Misc Setup

@bot.command()
async def help(ctx):
    help_str = "Commands:\n"
    help_str += "+\t,notify <true|false>\n\t\t// activates or deactivates notifications\n"
    help_str += "+\t,color\n\t\t// get a colour!\n"
    help_str += "+\t,ping\t\t\n\t\t// pong\n"
    help_str += "+\t,gamejam\n\t\t// lists the 8 most popular game jams from itch.io\n"
    help_str += "+\t,gamejam more\n\t\t// 16 most popular game jams from itch.io\n"
    help_str += "+\t,gamejam soon\n\t\t// lists 4 most popular game jams from itch.io running this week\n"
    help_str += "+\t,pleade\n\t\t// pleade to Cube Bot and ask for forgiveness if you have sinned\n"
    help_str += "\nInteraction:\n\tTry saying hi to Cube Bot"

    await ctx.send("```diff\n{}```".format(help_str))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="conway's game of life"))

    # apparently cogs need to be loaded from here now??
    await bot.load_extension("cogs.roles")
    await bot.load_extension("cogs.schedule")

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
    cleaned_msg_ascii_only = (cleaned_msg.encode('ascii', 'ignore')).decode("utf-8").strip()

    forgive_question_list = [
        "cubebot please forgive me", "cube bot please forgive me", "cube-bot please forgive me",
        "cubebot i ask for your forgiveness", "cube bot i ask for your forgiveness", "cube-bot i ask for your forgiveness",
        "cubebot will you forgive me?", "cube bot will you forgive me?", "cube-bot will you forgive me?",
        "cubebot can you forgive me?", "cube bot can you forgive me?", "cube-bot can you forgive me?",
    ]
    if cleaned_msg_ascii_only in forgive_question_list:
        pass # TODO: call the please command

    ends_with_myname = cleaned_msg_ascii_only.endswith(mynames[0].lower()) \
                     or cleaned_msg_ascii_only.endswith(mynames[1].lower()) \
                     or cleaned_msg_ascii_only.endswith(mynames[2].lower())
    if ends_with_myname and len(cleaned_msg_ascii_only) > 9 and cleaned_msg_ascii_only[:-8].strip() in greetings:
        end_char = "!" if random.randint(0, 1) == 1 else ""
        await message.channel.send("{} {}{}".format(random.choice(greetings), message.author.mention, end_char))
    elif "linux" in cleaned_msg_ascii_only and (not "gnu linux" in cleaned_msg_ascii_only) and (not "gnulinux" in cleaned_msg_ascii_only):
        await message.channel.send("you mean GNU linux, right?")
    
    # if player mentions a banned word, "ban them"
    if "fuck" in cleaned_msg_ascii_only and len(cleaned_msg_ascii_only) < 10:
        await message.channel.send("language {}! this is a christian minecraft server".format(message.author.mention))
    elif "video game" in cleaned_msg_ascii_only:
        message_author_role_names = [y.name for y in message.author.roles]
        if not "BANNED" in message_author_role_names:
            await message.channel.send("!! intolerable conduct detected, issuing appropriate punishment !!")
            r = discord.utils.get(message.guild.roles, name="BANNED")
            if r: await message.author.add_roles(r)
        elif ("BANNED" in message_author_role_names) and (not "SUPER_BANNED" in message_author_role_names): 
            await message.channel.send("that was a mistake {}".format(message.author.mention))
            await message.channel.send("!!! {}, issuing MAXIMUM punishment !!!".format( random.choice(["T̴̡̪͘Ḧ̴͎̝́̇E̸̝̾Ÿ̶͙́ ̷̟̝̎͝N̴͓̻̉E̵̗̙̾́V̵͖͝Ë̷͕́̅Ŕ̸̙͓ ̴͔͐̄L̸͖̟̓E̸̛͓͆Å̸̯͇Ŗ̶͛͌N̴̥͝", "T̶̻̔H̷͓̮̅̅E̸̻̝̍Y̵̪͐͂͜ ̵̛̱N̷̝̿̆E̵̘͘V̸̹̳̅̌E̵͙͕͌Ṟ̵̙̄̊ ̸̯͛͘L̴̲̪͋̈́E̶̢̖̍̄A̵͖̥͂R̷̳͉̾Ǹ̵̛͓̜", "Ṱ̷͌Ḧ̷̼́E̷͔͌Ỷ̶͍ ̸̤̄N̷̮̉E̵͓̕V̷̗̏Ḙ̶͊R̵̺̂ ̵̧̉L̵̳̉E̵͕̓Â̴̠R̸̪̿N̸̘̈́", "T̸̢̈́H̴͎̀E̴͎̒Ỵ̶̍ ̸̛͕N̴͔̅E̶͓̊V̴̞͝E̷͐͜R̸̭͝ ̸̨́L̷͕̿Ȇ̵ͅA̵̻͌R̴̠̕N̴͈̈́"]) ))
            r = discord.utils.get(message.guild.roles, name="SUPER_BANNED")
            if r: await message.author.add_roles(r)
        elif ("BANNED" in message_author_role_names) and ("SUPER_BANNED" in message_author_role_names): 
            await message.channel.send("{} {}".format(message.author.mention, "(っ◔◡◔)っ ♥ SILENCE ♥" if random.random() > 0.99 else "🆂🅸🅻🅴🅽🅲🅴"))

    # Adding to Honorary Tom Cruise role to people who post in #missions
    guild = bot.get_guild(int(os.environ["MAIN_SERVER_ID"]))
    if message.channel.id == missions_channel_id and not honorary_tom_cruise_id in [role.id for role in message.author.roles]:
        tom_cruise_role = get(guild.roles, id=honorary_tom_cruise_id)
        await message.author.add_roles(tom_cruise_role)
        await message.channel.send(f"Welcome to **Monthly Missions**, {message.author.name}!\n\n" 
                                   + "You have now been given the `Honorary Tom Cruise` role, since you will be engaging in Missions that may seem Impossible each month. "
                                   + "(Also this lets us ping all **Monthly Missions** members)\n\n"
                                   + "If you don't want to be an `Honorary Tom Cruise` any more, contact an executive and they can remove the role!")

# --------------------------------------------------------------------------- #
# New Users

@bot.event
async def on_member_join(member):
    guild = bot.get_guild(int(os.environ["MAIN_SERVER_ID"]))
    channel = discord.utils.get(guild.channels, name="bot-spam")
    await channel.send("Welcome {}! To get started, go to #roles and grab a fancy name colour!".format(member.mention))
    await channel.send("Our goal is to set all Game Developers at SFU up for success, regardless of if you have experience or not! Please show off projects you're working on, no matter how polished they are :)\n\nCheck out the events tab in Discord for events we run; hope to see you stop by!")

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