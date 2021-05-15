import asyncio
import discord
from discord.ext import commands, tasks

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
            await message.add_reaction(emoji=":gameboy:")
            await message.add_reaction(emoji=":bulbasaur:")
            is_gameboy = lambda reaction, user: user == ctx.message.author and str(reaction.emoji) == ':gameboy:'
            is_bulbasaur = lambda reaction, user: user == ctx.message.author and str(reaction.emoji) == ':bulbasaur:'
            check = lambda r, u: is_gameboy(r,u) or is_bulbasaur(r,u)
 
            # wait for reponse or timeout
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)
                if reaction.emoji == ":bulbasaur:":
                    role = discord.utils.get(ctx.guild.roles, name="Bulbasaur Green")
                    await user.add_roles(role)
                elif reaction.emoji == ":gameboy:":
                    role = discord.utils.get(ctx.guild.roles, name="Gameboy Yellow")
                    await user.add_roles(role)             
            except asyncio.TimeoutError:
                await ctx.send('You took too long, try again.')
            else:
                role = discord.utils.get(ctx.guild.roles, name="Notification Squad")
                await ctx.message.author.add_roles(role)
                await ctx.send("Enjoy {}!".format(reaction.emoji))

        elif val == "false":
            # remove roles if possible
            user = ctx.message.author
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
    
    #@notify.error
    #async def notify_error():
    #    pass
    

# --------------------------------------------------------------------------- #

def setup(bot):
    bot.add_cog(Roles(bot))
    print("cog loaded")