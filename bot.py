from importlib.machinery import ModuleSpec
import os, asyncio, requests, json, time
from datetime import datetime, timedelta
from discord.ext import commands
import logging, logging.handlers
from utils.functions import *
import discord, sqlite3, sys
import operator, re, random

logger = logging.getLogger("jamubot")
log_format = logging.Formatter(
    '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
    '%(message)s',
    datefmt="[%d/%m/%Y %H:%M]")
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(log_format)
logger.setLevel(logging.WARNING)
logger.addHandler(stdout_handler)

class Jamubot(commands.AutoShardedBot):
    async def on_ready(self):
        print('Logged in as {}\nI can see {} users in {} servers'.format(
            self.user,  len(list(self.get_all_members())), 
            len(self.guilds)))
        self.uptime = datetime.now()
        for cog in settings['cogs']:
            try:
                self.load_extension(cog)
            except Exception as e:
                print('Failed to load cog {}\n{}: {}'.format(cog, type(e).__name__, e))

# Bot setup
settings = json.loads(open('settings.json', 'r').read())
jamubot = Jamubot(settings['prefix'])
jamubot.settings = settings
jamubot.database = sqlite3.connect('database.db')
c = jamubot.database.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (discordid INTEGER, osuid INTEGER, mode INTEGER, skin TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS times (osuid INTEGER, joined TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS maps (mapid INTEGER, mapfile TEXT, maplink TEXT, pp REAL, stars REAL, style REAL, creator TEXT, mode INTEGER, ar REAL, od REAL, cs REAL, mods TEXT, graph TEXT)")

jamubot.emotes = {
    'bingCry': '<:bingCry:357902720767885312>', 'bingAw': '<:bingAw:357902800203546625>', 
    'bingCute': '<:bingCute:357902804893040641>', 'cirCop': '<:cirCop:357902818163556352>', 
    'bingShy': '<:bingShy:357902823880523776>', 'bingFeels': '<:bingFeels:357902852716494848>', 
    'bingHeart': '<:bingHeart:357902863772418048>', 'cirBlech': '<:cirBlech:357902870395486208>', 
    'bingGasm': '<:bingGasm:357902871108255744>', 'bingLurk': '<:bingLurk:357902872182128641>', 
    'bingShrug': '<:bingShrug:357902872794628097>', 'bingPeek': '<:bingPeek:357902872924389376>', 
    'bingWTF': '<:bingWTF:357902873931153418>', 'bingT': '<:bingT:357902873939673088>', 
    'bingYay': '<:bingYay:357902874497253377>', 'bingHey': '<:bingHey:357902875235581952>', 
    'bingLove': '<:bingLove:357902876049145856>', 'bakaYuu': '<:bakaYuu:357904206843084810>'
}

# For osu api limit setup
jamubot.currentrequests = 0
jamubot.lastrequestreset = time.perf_counter()

@jamubot.command(hidden=True)
async def load(ctx, cog):
    """Loads an extension."""
    if ctx.message.author.id in jamubot.settings['devs']:
        try:
            jamubot.load_extension(cog)
        except Exception as e:
            await ctx.message.channel.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.message.channel.send("{} loaded.".format(cog))

@jamubot.command(hidden=True)
async def unload(ctx, cog):
    """Unloads an extension."""
    if ctx.message.author.id in jamubot.settings['devs']:
        jamubot.unload_extension(cog)
        await ctx.message.channel.send("{} unloaded.".format(cog))

@jamubot.command(hidden=True)
async def reload(ctx, cog):
    """Reloads an extension."""
    if ctx.message.author.id in jamubot.settings['devs']:
        jamubot.unload_extension(cog)
        try:
            jamubot.load_extension(cog)
        except Exception as e:
            await ctx.message.channel.send("```py\n{}: {}```".format(type(e).__name__, str(e)))
            return
        await ctx.message.channel.send("{} reloaded.".format(cog))

@jamubot.command(hidden=True)
async def debug(ctx, *, code):
    """Evaluates code"""
    if ctx.message.author.id == 103139260340633600:
        author = ctx.message.author
        channel = ctx.message.channel
        code = code.strip('` ')
        result = None
        global_vars = globals().copy()
        global_vars['bot'] = jamubot
        global_vars['ctx'] = ctx
        global_vars['message'] = ctx.message
        global_vars['author'] = ctx.message.author
        global_vars['channel'] = ctx.message.channel
        global_vars['server'] = ctx.message.guild
        try:
            result = eval(code, global_vars, locals())
        except Exception as e:
            await channel.send("```py\n{}: {}```".format(type(e).__name__, str(e)))
            return
        if asyncio.iscoroutine(result):
            result = await result
        await channel.send("```py\n{}```".format(str(result)))

@jamubot.event
async def on_command_error(ctx, error):
    message = ("Error in command '{}'.\n```{}```".format(ctx.command.qualified_name, error))
    await ctx.message.channel.send(message)
    await jamubot.get_channel(379147907011706900).send(message)

# Starts the bot
jamubot.run(settings['token'])
# Saves and closes the database after bot is done running
jamubot.database.commit()
jamubot.database.close()