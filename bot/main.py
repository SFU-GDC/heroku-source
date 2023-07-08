import os, random
from datetime import datetime

import discord
from discord.ext import commands, tasks
from discord.utils import get

from myconstants import greetings, mynames, missions_channel_id, honorary_tom_cruise_id, game_jam_emote_name, game_jam_role

import db_manager, util

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
    help_str = "Commands:\n\t"
    help_str += ",notify <true|false>\n\t\t// activates or deactivates notifications\n\t"
    help_str += ",color\n\t\t// get a colour!\n\t"
    help_str += ",ping\t\t\n\t\t// pong\n\t"
    help_str += ",gamejam\n\t\t// lists the 8 most popular game jams from itch.io\n\t"
    help_str += ",gamejam more\n\t\t// 16 most popular game jams from itch.io\n\t"
    help_str += ",gamejam soon\n\t\t// lists 4 most popular game jams from itch.io running this week\n\t"
    help_str += ",events\n\n\n"
    help_str += ",meetings\n\t\t// shows upcoming club events\n\n"
    help_str += "Interaction:\n\tTry saying hi to Cube Bot"
    await ctx.send("```{}```".format(help_str))

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
        #try:
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

    # hi patrick
    guild = bot.get_guild(int(os.environ["MAIN_SERVER_ID"]))
    channel = discord.utils.get(guild.channels, name="bot-test")
    await channel.send("hi <@253596979085574144>")

JAM_ROLES_MESSAGE_ID = 1124602646150533130

async def add_role(user, roles, name):
    r = discord.utils.get(roles, name=name)
    print("toget: {}".format(name))
    print("role: {}".format(r))
    if r: 
        await user.add_roles(r)
        print("done adding role")

#JAM_ROLES_CHANNEL_ID = 1124067242653516006
'''
@bot.event
async def on_reaction_add(reaction, user):
    print("reaction occured {}".format(reaction.emoji.name))
    channel = bot.get_channel(JAM_ROLES_CHANNEL_ID)
    if reaction.message.channel.id == channel.id and reaction.emoji.name == game_jam_emote_name:
        await add_role(user, user.server.roles, game_jam_role)
'''

# REACT WITH :GAMEJAM: TO GET THE MOUNTAIN-TOP-JAMMER ROLE
@bot.event
async def on_raw_reaction_add(payload):
    print("RAW reaction occured {}".format(payload.emoji.name))
    print("payload.event_type {}".format(payload.event_type))
    print("payload.guild_id {}".format(payload.guild_id))
    print("payload.message_id {}".format(payload.message_id))
    print("payload.member {}".format(payload.member))
    print("payload.member.guild {}".format(payload.member.guild))
    print("payload.member.guild.roles {}".format(payload.member.guild.roles))
    #channel = bot.get_channel(JAM_ROLES_CHANNEL_ID)
    if payload.message_id == JAM_ROLES_MESSAGE_ID and payload.emoji.name == game_jam_emote_name:
        print("inner")
        await add_role(payload.member, payload.member.guild.roles, game_jam_role)

# --------------------------------------------------------------------------- #
# New Users

@bot.event
async def on_member_join(member):
    guild = bot.get_guild(int(os.environ["MAIN_SERVER_ID"]))
    channel = discord.utils.get(guild.channels, name="bot-spam")
    await channel.send("Welcome {}! To get started, try doing `,color` (do `,color` i dare you; it actually works now!)".format(member.mention))
    await channel.send("As a club we want to set Game Developers at SFU up for success, regardless of if you have experience or not! Please show off projects you're working on, no matter how polished they are :)\n\nCheck out the events tab in Discord for events we run; hope to see you stop by!")
    
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