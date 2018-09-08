import discord, asyncio, aiohttp
from discord.ext import commands
from datetime import datetime
from libs import pyttanko
import os, re


class Tracker:
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def track(self, *args):
        print(args)

    @track.command()
    async def add(self, ctx, *usernames):
        await ctx.send(str(usernames))


def setup(bot):
    n = Tracker(bot)
    bot.add_cog(n)
