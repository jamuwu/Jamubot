import os, asyncio, requests, json, time
import operator, re, random, aiohttp
from datetime import datetime, timedelta
import discord, sqlite3
from discord.ext import commands
from utils.functions import *

class Essential:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def uptime(self, ctx):
        timeago = await time_ago(datetime.now(), self.bot.uptime)
        await ctx.message.channel.send(timeago.replace('*', ''))

    async def dblpost(self):
        headers = {'Authorization': self.bot.settings['dbltoken']}
        data = {'server_count': len(self.bot.guilds)}
        async with aiohttp.ClientSession() as session:
            req = await session.post('https://discordbots.org/api/bots/{}/stats'.format(self.bot.user.id), data=data, headers=headers)

    async def on_guild_join(self, guild):
        info  = "Owner: {}#{}\n".format(guild.owner.name, guild.owner.discriminator)
        info += "Users: {}\n".format(len([u for u in guild.members if not u.bot]))
        info += "Bots:  {}\n".format(len([u for u in guild.members if u.bot]))
        info += "New Server Count: {}".format(len(self.bot.guilds))
        em = discord.Embed(description=info)
        em.set_author(name="I was just added to {}".format(guild.name))
        await self.bot.get_channel(382552600563941376).send(embed=em)
        await self.dblpost()

    async def on_guild_remove(self, guild):
        info = "New Server Count: {}".format(len(self.bot.guilds))
        em = discord.Embed(description=info)
        em.set_author(name="I was just removed from {}".format(guild.name))
        await self.bot.get_channel(382552600563941376).send(embed=em)
        await self.dblpost()

    @commands.command(hidden=True)
    async def chan(self, ctx):
        await ctx.message.channel.send(ctx.message.channel.id)

    @commands.command()
    async def ping(self, ctx):
        """Shows the bots ping in ms"""
        t1 = time.perf_counter()
        await ctx.message.channel.trigger_typing()
        t2 = time.perf_counter()
        await ctx.message.channel.send("**Pong.**\nTook {}ms.".format(round((t2-t1)*1000)))

def setup(bot):
    bot.add_cog(Essential(bot))