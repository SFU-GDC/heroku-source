import asyncio
import discord
from discord.ext import commands, tasks

from myconstants import bulbasaur_green, gameboy_yellow

# For the notification roles

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx): # This was inside '__init__' before
        await ctx.send("pong!\n{}ms".format(round(self.bot.latency * 1000)))

    @commands.command()
    async def notify(self, ctx, activate):
        print("notify")
        val = str(activate).lower()
        if val == "true":
            await ctx.send("You will now recieve notifications")
            message = await ctx.send("Choose a colour by reacting to this message")
            await message.add_reaction(emoji=bulbasaur_green)
            await message.add_reaction(emoji=gameboy_yellow)
            is_bulbasaur = lambda reaction, user: user == ctx.message.author and str(reaction.emoji) == bulbasaur_green
            is_gameboy = lambda reaction, user: user == ctx.message.author and str(reaction.emoji) == gameboy_yellow
            check = lambda r, u: is_gameboy(r,u) or is_bulbasaur(r,u)
    
            role = discord.utils.get(ctx.guild.roles, name="Notification Squad")
            role = ctx.message.author.add_roles(role)

            # wait for reponse or timeout
            try:
                print("waiting")
                print(ctx.guild.roles)
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=45.0)
                user = ctx.message.author

                print("react")
                print(reaction.emoji)
                print(reaction.emoji.id)
                print(reaction.emoji.name)
                if reaction.emoji.name == "Bulbasaur Green":
                    role = discord.utils.get(ctx.guild.roles, name="Bulbasaur Green")
                    print(role)
                    await user.add_roles(role)
                elif reaction.emoji.name == "Gameboy Yellow":
                    role = discord.utils.get(ctx.guild.roles, name="Gameboy Yellow")
                    await user.add_roles(role)             
            except asyncio.TimeoutError:
                await ctx.send('You took too long, try again.')
            else:
                print("end")

                await ctx.send("Enjoy {}!".format(reaction.emoji))

        elif val == "false":
            # remove roles if possible
            user = ctx.message.author
            print(user.roles)
            if "Bulbasaur Green" in user.roles:
                role = discord.utils.get(ctx.guild.roles, name="Bulbasaur Green")
                await user.add_roles(role)

            if "Gameboy Yellow" in user.roles:
                role = discord.utils.get(ctx.guild.roles, name="Gameboy Yellow")
                await user.add_roles(role)

            if "Notification Squad" in user.roles:
                role = discord.utils.get(ctx.guild.roles, name="Notification Squad")
                await user.add_roles(role)

            await ctx.send("You will no longer recieve notifications")
        else:
            await ctx.send("Error: please type `,notify true` or `,notify false`")
    
    @notify.error
    async def notify_error(self, ctx, error):
        print("error: {}".format(repr(error)))
        await ctx.send("Oops, something went wrong. Call the function like this: `,notify true`")
    

# --------------------------------------------------------------------------- #

def setup(bot):
    bot.add_cog(Roles(bot))