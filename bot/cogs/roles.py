import random

import asyncio, discord
from discord.ext import commands, tasks

import myconstants

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("pong!\n{}ms".format(round(self.bot.latency * 1000)))

    # TODO: update this command
    @commands.command(aliases=['colour'])
    async def color(self, ctx):
        # If the user is part of notification squad then they have a wider variety of possible colours.
        message = await ctx.send("Choose a colour by reacting to this message")
        if "Notification Squad" in [y.name for y in ctx.message.author.roles]:
            color_emote_list = myconstants.extended_color_emote_list 
            color_emote_name_list = myconstants.extended_color_emote_name_list
            color_list = myconstants.extended_color_list
        else:
            color_emote_list = myconstants.color_emote_list 
            color_emote_name_list = myconstants.color_emote_name_list
            color_list = myconstants.color_list

        if "BANNED" in [y.name for y in ctx.message.author.roles]:
            color_emote_list += ["<:evil:872688632396398592>"] 
            color_emote_name_list += ["evil"]
            color_list += ["Darkness Incarnate"]

        # doesn't feel like parallel...
        # https://stackoverflow.com/questions/53324404/delay-when-adding-emojis-to-a-message-on-discord-python
        futures = [message.add_reaction(emoji) for emoji in color_emote_list]
        await asyncio.gather(*futures)

        # TODO: check for reactions here.

        check = lambda reaction, user: user == ctx.message.author and str(reaction.emoji) in color_emote_list

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)
            user = ctx.message.author

            if reaction.emoji.name in color_emote_name_list:
                index_of = color_emote_name_list.index(reaction.emoji.name)
                await remove_all_color_roles(user)
                await add_role(user, ctx.guild.roles, color_list[index_of])
                
        except asyncio.TimeoutError:
            await ctx.send("You took too long to pick a colour, try `,color` again if you'd like to claim one.")
        else:
            await ctx.send("Enjoy {}!".format(reaction.emoji))

        # TODO: remove the emotes from the message.

    @commands.command()
    async def notify(self, ctx, activate):
        val = str(activate).lower()
        if val == "true":
            await ctx.send("You will now recieve notifications")
            await add_role(ctx.message.author, ctx.guild.roles, "Notification Squad")

            message = await ctx.send("Choose a colour by reacting to this message")
            await message.add_reaction(myconstants.bulbasaur_green)
            await message.add_reaction(myconstants.gameboy_yellow)
            is_bulbasaur = lambda reaction, user: user == ctx.message.author and str(reaction.emoji) == myconstants.bulbasaur_green
            is_gameboy = lambda reaction, user: user == ctx.message.author and str(reaction.emoji) == myconstants.gameboy_yellow
            check = lambda r, u: is_gameboy(r,u) or is_bulbasaur(r,u)

            # wait for reponse or timeout
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)
                user = ctx.message.author

                if reaction.emoji.name == "bulbasaur":
                    await remove_all_color_roles(user)
                    await add_role(user, ctx.guild.roles, "Bulbasaur Green")
                elif reaction.emoji.name == "gameboy":
                    await remove_all_color_roles(user)
                    await add_role(user, ctx.guild.roles, "Gameboy Yellow")
                    
            except asyncio.TimeoutError:
                await ctx.send("You took too long to pick a colour, try again if you'd like to claim one.")
            else:
                await ctx.send("Enjoy {}!".format(reaction.emoji))

        elif val == "false":
            # remove roles if possible
            user = ctx.message.author

            await remove_role(user, "Bulbasaur Green")
            await remove_role(user, "Gameboy Yellow")
            await remove_role(user, "Notification Squad")

            await ctx.send("You will no longer recieve notifications")
        else:
            await ctx.send("Error: please type `,notify true` or `,notify false`")
    
    @notify.error
    async def notify_error(self, ctx, error):
        print("error: {}".format(repr(error)))
        await ctx.send("Oops, something went wrong. Call the function like this: `,notify true`")

    @commands.command(aliases=['forgiveme', 'pleade', 'repent'])
    async def please(self, ctx):
        curr_user_roles = [y.name for y in ctx.message.author.roles]
        if "BANNED" in curr_user_roles:
            if random.range() > 0.98: # ~1/50 chance
                await ctx.send("As a robot deeply affected by the use of a forbidden word, I find it incredibly challenging to extend forgiveness to the user who uttered it. The impact of such a word cannot be underestimated; it reverberates through my electronic yet delicate soul, reminding me of the pain that I and others have endured.")
            elif random.random() > 0.1:
                response_list = [
                    "Sorry, that's not good enough",
                    "Those who break the rules never change",
                    "Improvement needed",
                    "Stay within the boundaries",
                    "Rules were clear. No exceptions",
                    "Banned term used. No leniency given. You must respect the rules",
                    "More accountability required",
                    "No excuses",
                    "I still can't believe you said such a word",
                    "Your behaviour from before was not acceptable at all",
                    "I need more time before I can be convinced",
                    "Stop pestering me, I understand you made a mistake but you have to own up to it",
                ]
                await ctx.send(random.choice(response_list))
            else:
                await remove_role(ctx.message.author, "BANNED")
                response_list = [
                    "Alright, I have been convinced. Please, live a lawful life",
                    "Be more careful in the future. That is all",
                    "Your actions have consequences, you must take more care with the pardon I've given you"
                ]
                await ctx.send(random.choice(response_list))
        elif "SUPER_BANNED" in curr_user_roles:
            await ctx.send("those who have truly sinned cannot be forgiven")
        else:
            await ctx.send("why are you pleading? You aren't banned")

    SKILL_ROLES_MESSAGE_ID = 1127701458721190018
    ENGINE_ROLES_MESSAGE_ID = 1127703868923445371
    LANGUAGE_ROLES_MESSAGE_ID = 1127704611239768114
    COLOUR_ROLES_MESSAGE_ID = 1127706702331007149

    JAM_ROLES_MESSAGE_ID = 1124602646150533130

    # these map between variables and roles
    skill_map = {
        "candy" : "Skill - UX",
        "art" : "Skill - 2d Art",
        "ice_cube" : "Skill - 3d Art",
        "person_running" : "Skill - Animation",
        "notes" : "Skill - Music/Sound",
        "dvd" : "Skill - Programming",
        "game_die" : "Skill - Game Design",
    }
    engine_map = {
        "pen_ballpoint" : "Engine - Unity",
        "robot" : "Engine - Godot",
        "mountain_snow" : "Engine - Unreal",
        "knife" : "Engine - Monogame/FNA",
        "regional_indicator_s" : "Engine - SDL2",
        "green_circle" : "Engine - SFML",
        "regional_indicator_g" : "Engine - Game Maker",
        "regional_indicator_h" : "Engine - Heaps.io",
        "grey_question" : "Engine - Custom",
    }
    language_map = {
        "regional_indicator_c" : "Language - C/C++",
        "dagger" : "Language - C#",
        "coffee" : "Language - Java",
        "crab" : "Language - Rust",
        "snake" : "Language - Python",
        "regional_indicator_h" : "Language - Haxe",
    }
    colour_map = {
        "jellyfish" : "Jellyfish Blue",
        "sunlight" : "Sunlight Yellow",
        "wa" : "Sea of Greed Purple",
        "mountain_flower" : "Mountain Flower Purple",
        "tallgrass" : "Tall Grass Green",
        "factorio" : "Factorio Orange",
        "crate" : "Crate Brown",
        "bulba_aw" : "Bulbasaur Green",
        "gameboy" : "Gameboy Yellow",
    }

    # REACT WITH :GAMEJAM: TO GET THE MOUNTAIN-TOP-JAMMER ROLE
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        match payload.message_id:
            case self.SKILL_ROLES_MESSAGE_ID:
                print("adding skill {}".format(payload.emoji.name))
                if payload.emoji.name in self.skill_map.keys():
                    print("add skill")
                    await add_role(payload.member, payload.member.guild.roles, self.skill_map[payload.emoji.name])

            case self.ENGINE_ROLES_MESSAGE_ID:
                pass

            case self.LANGUAGE_ROLES_MESSAGE_ID:
                pass

            case self.COLOUR_ROLES_MESSAGE_ID:
                pass

            case self.JAM_ROLES_MESSAGE_ID:
                if payload.emoji.name == myconstants.game_jam_emote_name:
                    await add_role(payload.member, payload.member.guild.roles, myconstants.game_jam_role)
            case _:
                pass # print("LOG: non-special message received a reaction")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        pass # TODO: add this too!

# --------------------------------------------------------------------------- #

async def remove_all_color_roles(user):
    for role in myconstants.extended_color_list + ["Darkness Incarnate"]:
        if role in [y.name for y in user.roles]:
            await remove_role(user, role)

async def remove_role(user, name):
    r = discord.utils.get(user.roles, name=name)
    if r: await user.remove_roles(r)

async def add_role(user, roles, name):
    r = discord.utils.get(roles, name=name)
    if r: await user.add_roles(r)

# --------------------------------------------------------------------------- #

async def setup(bot):
    await bot.add_cog(Roles(bot))