import discord, asyncio, aiohttp
from discord.ext import commands
from datetime import datetime
from libs import pyttanko
import os, re


class Tracker:
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    n = Tracker(bot)
    bot.add_cog(n)
