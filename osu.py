import os, asyncio, requests, json, time
import operator, re, random
from datetime import datetime
import discord, sqlite3
from discord.ext import commands
from utils.functions import *
from utils.osuapi import *
from utils import pyttanko

# Sets up for matplotlib
import matplotlib as mpl
mpl.use('Agg') # for non gui
import matplotlib.pyplot as plt
from matplotlib import ticker

class Osu:
    def __init__(self, bot):
        self.jamubot = bot
        self.maps = {}
        self.weighted_choice = lambda s : random.choice(sum(([v]*wt for v,wt in s),[]))

    @commands.command()
    async def osu(self, ctx, *content):
        """Shows Standard stats."""
        content = list(content)
        if len(content) < 1:
            c = self.jamubot.database.cursor()
            record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
            if len(record) < 1:
                await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
                return
            else:
                content = [record[0][0]]
        for i in range(len(content)):
            await self.checkrequests()
            userinfo = await get_user(self.jamubot.settings['key'], content[i], 0)
            if len(userinfo) == 0:
                await ctx.message.channel.send("{} not found! {}".format(content[i], self.jamubot.emotes['bingCry']))
                return
            await ctx.message.channel.send(embed=await self.profile_embed(userinfo[0], 'Standard'))

    @commands.command()
    async def taiko(self, ctx, *content):
        """Shows Taiko stats."""
        content = list(content)
        if len(content) < 1:
            c = self.jamubot.database.cursor()
            record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
            if len(record) < 1:
                await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
                return
            else:
                content = [record[0][0]]
        for i in range(len(content)):
            await self.checkrequests()
            userinfo = await get_user(self.jamubot.settings['key'], content[i], 1)
            if len(userinfo) == 0:
                await ctx.message.channel.send("{} not found! {}".format(content[i], self.jamubot.emotes['bingCry']))
                return
            await ctx.message.channel.send(embed=await self.profile_embed(userinfo[0], 'Taiko'))

    @commands.command()
    async def ctb(self, ctx, *content):
        """Shows CTB stats."""
        content = list(content)
        if len(content) < 1:
            c = self.jamubot.database.cursor()
            record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
            if len(record) < 1:
                await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
                return
            else:
                content = [record[0][0]]
        for i in range(len(content)):
            await self.checkrequests()
            userinfo = await get_user(self.jamubot.settings['key'], content[i], 2)
            if len(userinfo) == 0:
                await ctx.message.channel.send("{} not found! {}".format(content[i], self.jamubot.emotes['bingCry']))
                return
            await ctx.message.channel.send(embed=await self.profile_embed(userinfo[0], 'CTB'))

    @commands.command()
    async def mania(self, ctx, *content):
        """Shows Mania stats."""
        content = list(content)
        if len(content) < 1:
            c = self.jamubot.database.cursor()
            record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
            if len(record) < 1:
                await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
                return
            else:
                content = [record[0][0]]
        for i in range(len(content)):
            await self.checkrequests()
            userinfo = await get_user(self.jamubot.settings['key'], content[i], 3)
            if len(userinfo) == 0:
                await ctx.message.channel.send("{} not found! {}".format(content[i], self.jamubot.emotes['bingCry']))
                return
            await ctx.message.channel.send(embed=await self.profile_embed(userinfo[0], 'Mania'))

    @commands.command()
    async def osud(self, ctx, *content):
        """Shows detailed Standard stats."""
        content = list(content)
        if len(content) < 1:
            c = self.jamubot.database.cursor()
            record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
            if len(record) < 1:
                await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
                return
            else:
                content = [record[0][0]]
        for i in range(len(content)):
            await self.checkrequests()
            userinfo = await get_user(self.jamubot.settings['key'], content[i], 0)
            if len(userinfo) == 0:
                await ctx.message.channel.send("{} not found! {}".format(content[i], self.jamubot.emotes['bingCry']))
                return
            await ctx.message.channel.send(embed=await self.det_prof_embed(userinfo[0], 'Standard', 0))

    #@commands.command()
    #async def taikod(self, ctx, *content):
    #    """Shows detailed Taiko stats."""
    #    content = list(content)
    #    if len(content) < 1:
    #        c = self.jamubot.database.cursor()
    #        record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
    #        if len(record) < 1:
    #            await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
    #            return
    #        else:
    #            content = [record[0][0]]
    #    for i in range(len(content)):
    #        await self.checkrequests()
    #        userinfo = await get_user(self.jamubot.settings['key'], content[i], 1)
    #        if len(userinfo) == 0:
    #            await ctx.message.channel.send("{} not found! {}".format(content[i], self.jamubot.emotes['bingCry']))
    #            return
    #        await ctx.message.channel.send(embed=await self.det_prof_embed(userinfo[0], 'Taiko', 1))

    #@commands.command()
    #async def ctbd(self, ctx, *content):
    #    """Shows detailed CTB stats."""
    #    content = list(content)
    #    if len(content) < 1:
    #        c = self.jamubot.database.cursor()
    #        record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
    #        if len(record) < 1:
    #            await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
    #            return
    #        else:
    #            content = [record[0][0]]
    #    for i in range(len(content)):
    #        await self.checkrequests()
    #        userinfo = await get_user(self.jamubot.settings['key'], content[i], 2)
    #        if len(userinfo) == 0:
    #            await ctx.message.channel.send("{} not found! {}".format(content[i], self.jamubot.emotes['bingCry']))
    #            return
    #        await ctx.message.channel.send(embed=await self.det_prof_embed(userinfo[0], 'CTB', 2))

    #@commands.command()
    #async def maniad(self, ctx, *content):
    #    """Shows detailed Mania stats."""
    #    content = list(content)
    #    if len(content) < 1:
    #        c = self.jamubot.database.cursor()
    #        record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
    #        if len(record) < 1:
    #            await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
    #            return
    #        else:
    #            content = [record[0][0]]
    #    for i in range(len(content)):
    #        await self.checkrequests()
    #        userinfo = await get_user(self.jamubot.settings['key'], content[i], 3)
    #        if len(userinfo) == 0:
    #            await ctx.message.channel.send("{} not found! {}".format(content[i], self.jamubot.emotes['bingCry']))
    #            return
    #        await ctx.message.channel.send(embed=await self.det_prof_embed(userinfo[0], 'Mania', 3))

    @commands.command()
    async def osutop(self, ctx, *content):
        """Shows the top 5 Standard plays of a user."""
        content = list(content)
        if len(content) < 1:
            c = self.jamubot.database.cursor()
            record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
            if len(record) < 1:
                await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
                return
            else:
                content = [record[0][0]]
        for i in range(len(content)):
            await self.checkrequests()
            scores = await get_user_best(self.jamubot.settings['key'], content[i], 0, 5)
            await ctx.message.channel.send(embed=await self.scores_embed(content[i], scores, 'Standard', 0))

    # Leaving this because taiko should be implemented in pyttanko soon
    #@commands.command()
    #async def taikotop(self, ctx, *content):
    #    """Shows the top 5 Taiko plays of a user."""
    #    content = list(content)
    #    if len(content) < 1:
    #        c = self.jamubot.database.cursor()
    #        record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
    #        if len(record) < 1:
    #            await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
    #            return
    #        else:
    #            content = [record[0][0]]
    #    for i in range(len(content)):
    #        await self.checkrequests()
    #        scores = await get_user_best(self.jamubot.settings['key'], content[i], 1, 6)
    #        await ctx.message.channel.send(embed=await self.scores_embed(content[i], scores, 'Taiko', 1))

    @commands.command()
    async def top(self, ctx, scorenum=None, *content):
        """Shows a specific number of a users top plays."""
        # First check if it's a number, then if it's
        # 1-100, then we continue on
        if not scorenum or not scorenum.isdigit() or int(scorenum) < 1 or int(scorenum) > 100:
            await ctx.message.channel.send("Please specify a valid number 1 - 100\n")
            return
        content = list(content)
        if len(content) < 1:
            c = self.jamubot.database.cursor()
            record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
            if len(record) < 1:
                await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
                return
            else:
                content = [record[0][0]]
        for i in range(len(content)):
            await self.checkrequests()
            scores = await get_user_best(self.jamubot.settings['key'], content[i], 0, scorenum)
            self.maps[str(ctx.message.channel.id)] = scores[-1]['beatmap_id']
            await ctx.message.channel.send(embed=await self.score_embed(content[i], scores[-1], scorenum, 'Standard', 0))

    @commands.command()
    async def recent(self, ctx, user=None, number=None):
        """Shows the recent play of a user."""
        if not number:
            if user and user.isdigit():
                number = int(user)
                user = None
            else: number = 1
            if not user:
                c = self.jamubot.database.cursor()
                record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
                if len(record) < 1:
                    await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
                    return
                else:
                    user = record[0][0]
        elif number.isdigit():
            number = int(number)
            if number < 1 or number > 5:
                await ctx.message.channel.send("{} isn't a proper number between 1 and 5 {}".format(number, self.jamubot.emotes['bingCry']))
                return
        else: number = 1
        await self.checkrequests()
        recent = await get_user_recent(self.jamubot.settings['key'], user, 0)
        self.maps[str(ctx.message.channel.id)] = recent[0]['beatmap_id']
        await ctx.message.channel.send(embed=await self.recent_embed(user, recent, 'Standard', 0, number))

    @commands.command()
    async def recentmap(self, ctx, user=None):
        """Shows the recent play of a user."""
        if not user:
            c = self.jamubot.database.cursor()
            record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
            if len(record) < 1:
                await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
                return
            else:
                user = record[0][0]
        await self.checkrequests()
        recent = await get_user_recent(self.jamubot.settings['key'], user, 0)
        mods = pyttanko.mods_str(int(recent[0]['enabled_mods']))
        self.maps[str(ctx.message.channel.id)] = recent[0]['beatmap_id']
        await self.map_embed(ctx.message, recent[0]['beatmap_id'], 'b', modstr=mods, rec=1)

    @commands.command()
    async def nochoke(self, ctx, user=None):
        """Shows the top 5 plays of a users nochoke scores"""
        if not user:
            c = self.jamubot.database.cursor()
            record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
            if len(record) < 1:
                await ctx.message.channel.send("You either need to specify a username or run  `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
                return
            else:
                user = record[0][0]
        scores = await self.process_nochoke(user)
        await ctx.message.channel.send(embed=await self.scores_embed(user, scores[:5], 'Standard', 0, 'nochoke'))

    @commands.command()
    async def scores(self, ctx, mapid='', user=None, mode:int=0):
        """Shows the recent play of a user."""
        if mapid == '' or not mapid.isdigit():
            mapid = mapid.replace('https://osu.ppy.sh/b/', '')
            if not mapid.isdigit():
                await ctx.message.channel.send("It doesn't seem you've provided a valid mapid/maplink, to use this command you must do so. {}".format(self.jamubot.emotes['bingShrug']))
                return
        if not user:
            c = self.jamubot.database.cursor()
            record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
            if len(record) < 1:
                await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
                return
            else:
                user = record[0][0]
        scores = await get_scores(self.jamubot.settings['key'], mapid, user, mode)
        self.maps[str(ctx.message.channel.id)] = mapid
        await ctx.message.channel.send(embed=await self.map_scores_embed(user, scores, await self.mode_to_str(mode), mode, mapid))

    @commands.command()
    async def compare(self, ctx):
        """Checks for your scores on the last map in chat."""
        c = self.jamubot.database.cursor()
        record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
        if len(record) < 1:
            await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
            return
        else:
            user = record[0][0]
        chan = str(ctx.message.channel.id)
        if chan in self.maps:
            mapid = self.maps[chan]
        else:
            await ctx.message.channel.send("No recent maps in the channel.")
            return
        scores = await get_scores(self.jamubot.settings['key'], mapid, user, 0)
        await ctx.message.channel.send(embed=await self.map_scores_embed(user, scores, await self.mode_to_str(0), 0, mapid))

    @commands.command()
    async def recenttop(self, ctx, user=None, mode:int=0):
        """Shows the most recent top plays of a user."""
        if user and user.isdigit() and int(user) >=1 and int(user) <=3:
            mode = int(user)
            user = None
        if not user:
            c = self.jamubot.database.cursor()
            record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
            if len(record) < 1:
                await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
                return
            else:
                user = record[0][0]
                await self.checkrequests()
        scores = await get_user_best(self.jamubot.settings['key'], user, mode, 100)
        for i in range(len(scores)):
            scores[i]['number'] = i
        scores = sorted(scores, key=operator.itemgetter('date'), reverse=True)
        await ctx.message.channel.send(embed=await self.scores_embed(user, scores[:5], await self.mode_to_str(mode), mode, 'recent'))

    @commands.command()
    async def mostplayed(self, ctx, user=None, mode:int=0):
        """Shows the most played maps of a user."""
        if user and user.isdigit() and int(user) >=1 and int(user) <=3:
            mode = int(user)
            user = None
        if not user:
            c = self.jamubot.database.cursor()
            record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
            if len(record) < 1:
                await ctx.message.channel.send("You either need to specify a username or run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
                return
            else:
                user = record[0][0]
                await self.checkrequests()
        userinfo = await get_user(self.jamubot.settings['key'], user, mode)
        maps = await get_most_played(int(userinfo[0]['user_id']), mode)
        print(maps[0])
        await self.most_played_embed(ctx.message, userinfo[0], maps)

    @commands.command()
    async def recommend(self, ctx, number:int=1):
        """Tries to recommend a map you might enjoy."""
        c = self.jamubot.database.cursor()
        record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
        if len(record) < 1:
            await ctx.message.channel.send("You either need to run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
            return
        else:
            user = record[0][0]
            speed, aim, cs, ar, od, bpm, pp, moddict = await self.process_scores(user, 0, juststats=True)
            mods = [(mod, moddict[mod]) for mod in moddict.keys()]
            rmap, rnum = await self.get_rmap(style=speed/(speed+aim)*100, nmaps=number, pp=pp, ar=ar, od=od, cs=cs, mods=mods)
            for mapu in rmap:
                await self.map_embed(ctx.message, mapu[0], 'b', mapu[-1], rec=rnum)

    @commands.command()
    async def jumpmap(self, ctx):
        """Tries to recommend a jump map that is around your skill level"""
        c = self.jamubot.database.cursor()
        record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
        if len(record) < 1:
            await ctx.message.channel.send("You either need to run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
            return
        else:
            user = record[0][0]
            _, _, _, _, _, _, pp, _ = await self.process_scores(user, 0, juststats=True)
            jmap = await self.get_map('jump', pp)
            await self.map_embed(ctx.message, jmap[0][0], 'b', jmap[0][-1], rec=69)

    @commands.command()
    async def streammap(self, ctx):
        """Tries to recommend a stream map that is around your skill level"""
        c = self.jamubot.database.cursor()
        record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
        if len(record) < 1:
            await ctx.message.channel.send("You either need to run `{}userset [username]` {}".format(self.jamubot.settings['prefix'], self.jamubot.emotes['bingCry']))
            return
        else:
            user = record[0][0]
            _, _, _, _, _, _, pp, _ = await self.process_scores(user, 0, juststats=True)
            smap = await self.get_map('stream', pp)
            await self.map_embed(ctx.message, smap[0][0], 'b', smap[0][-1], rec=69)

    @commands.command()
    async def userset(self, ctx, user):
        """Allows you to set your osu username to your discord account."""
        await self.checkrequests()
        user = await get_user(self.jamubot.settings['key'], user, 0)
        if user == []:
            await ctx.message.channel.send("The Osu! api returned nothing.")
        c = self.jamubot.database.cursor()
        record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(ctx.message.author.id)).fetchall()
        if len(record) < 1:
            c.execute('INSERT INTO users (discordid, osuid, mode, skin) VALUES ({}, {}, {}, "{}")'.format(ctx.message.author.id, user[0]['user_id'], 0, ''))
        else:
            c.execute('UPDATE users SET osuid = ({}) WHERE discordid = ({})'.format(user[0]['user_id'], ctx.message.author.id))
        await ctx.message.channel.send("Successfully set your username to {} {}".format(user[0]['username'], self.jamubot.emotes['bingYay']))

    @commands.command(hidden=True)
    async def forceset(self, ctx, duser:discord.Member, ouser, mode:int=0, skin=''):
        if ctx.message.author.id in self.jamubot.settings['devs']:
            await self.checkrequests()
            ouser = await get_user(self.jamubot.settings['key'], ouser, 0)
            c = self.jamubot.database.cursor()
            record = c.execute('SELECT osuid FROM users WHERE discordid = {}'.format(duser.id)).fetchall()
            if len(record) < 1:
                c.execute('INSERT INTO users (discordid, osuid, mode, skin) VALUES ({}, {}, {}, "{}")'.format(duser.id, ouser[0]['user_id'], mode, ''))
            else:
                c.execute('UPDATE users SET osuid = ({}) WHERE discordid = ({})'.format(ouser[0]['user_id'], duser.id))
            await ctx.message.channel.send("Successfully set {}'s username to {} {}".format(duser.name, ouser[0]['username'], self.jamubot.emotes['bingLurk']))

    # various functions
    async def profile_embed(self, user, gamemode):
        levelint, levelpercent = divmod(float(user['level']), 1)
        info = "▸ **Global Rank:** #{} ({}#{})\n".format(user['pp_rank'], user['country'], user['pp_country_rank'])
        info += "▸ **Level:** {} ({:.2f}%)\n".format(int(levelint), levelpercent * 100)
        info += "▸ **Total PP:** {:.2f}\n".format(float(user['pp_raw']))
        info += "▸ **Hit Accuracy:** {:.2f}%\n".format(float(user['accuracy']))
        info += "▸ **Playcount:** {:,}\n".format(int(user['playcount']))
        c = self.jamubot.database.cursor()
        record = c.execute('SELECT joined FROM times WHERE osuid = {}'.format(user['user_id'])).fetchall()
        if len(record) < 1:
            page = await self.get_web("https://osu.ppy.sh/u/{}".format(user['user_id']))
            timestamp = re.findall('"join_date":"([0-9]{4}-[0-9]{2}-[0-9]{2})"', page)
            c.execute('INSERT INTO times (osuid, joined) VALUES ({}, "{}")'.format(user['user_id'], timestamp))
            joined = datetime.strptime(timestamp, '%Y-%m-%d')
        else:
            joined = datetime.strptime(record[0][0].split(' ')[0], '%Y-%m-%d')
        em = discord.Embed(description=info, colour=0x00FFC0)
        em.set_author(name="{} Profile for {}".format(gamemode, user['username']), icon_url='https://osu.ppy.sh/images/flags/{}.png'.format(user['country']), url='https://osu.ppy.sh/u/{}'.format(user['user_id']))
        em.set_thumbnail(url='https://a.ppy.sh/{}?{}'.format(user['user_id'], time.perf_counter()))
        em.set_footer(text='Joined')
        em.timestamp = joined
        return em

    async def det_prof_embed(self, user, gamemode, modenum):
        levelint, levelpercent = divmod(float(user['level']), 1)
        totalhits = int(user['count50']) + int(user['count100']) + int(user['count300'])
        totalranks = int(user['count_rank_a']) + int(user['count_rank_s']) + int(user['count_rank_ss'])
        info = "▸ **Rank:** #{:,} ({}: {:,})\n".format(int(user['pp_rank']), user['country'], int(user['pp_country_rank']))
        info += "▸ **Level:** {} ({:.2f}%)\n".format(int(levelint), levelpercent * 100)
        info += "▸ **Total PP:** {:,.2f}\n".format(float(user['pp_raw']))
        info += "▸ **Hit Accuracy:** {:.2f}%\n".format(float(user['accuracy']))
        info += "▸ **Playcount:** {:,}\n".format(int(user['playcount']))
        info += "▸ **Total Hits:** {:,}\n".format(totalhits)
        info += "▸ **Ranked Score:** {:,}\n".format(int(user['ranked_score']))
        info += "▸ **Total Score:** {:,}\n".format(int(user['total_score']))
        c = self.jamubot.database.cursor()
        record = c.execute('SELECT joined FROM times WHERE osuid = {}'.format(user['user_id'])).fetchall()
        if len(record) < 1:
            page = await self.get_web("https://osu.ppy.sh/u/{}".format(user['user_id']))
            timestamp = re.findall('"join_date":"([0-9]{4}-[0-9]{2}-[0-9]{2})"', page)
            c.execute('INSERT INTO times (osuid, joined) VALUES ({}, "{}")'.format(user['user_id'], timestamp))
            joined = datetime.strptime(timestamp, '%Y-%m-%d')
        else:
            joined = datetime.strptime(record[0][0].split(' ')[0], '%Y-%m-%d')
        info += "▸ **300:** {:,} ({:.2f}%) ▸ **100:** {:,} ({:.2f}%) ▸ **50:** {:,} ({:.2f}%)\n".format(
            int(user['count300']), (int(user['count300']) / totalhits) * 100,
            int(user['count100']), (int(user['count100']) / totalhits) * 100,
            int(user['count50']), (int(user['count50']) / totalhits) * 100)
        info += "▸ **SS:** {:,} ({:.2f}%) ▸ **S:** {:,} ({:.2f}%) ▸ **A:** {:,} ({:.2f}%)\n".format(
            int(user['count_rank_ss']), (int(user['count_rank_ss']) / totalranks) * 100,
            int(user['count_rank_s']), (int(user['count_rank_s']) / totalranks) * 100,
            int(user['count_rank_a']), (int(user['count_rank_a']) / totalranks) * 100)        
        info += await self.process_scores(user['username'], modenum)
        em = discord.Embed(description=info, colour=0x00FFC0)
        em.set_author(name="Detailed {} Profile for {}".format(gamemode, user['username']), icon_url='https://osu.ppy.sh/images/flags/{}.png'.format(user['country']), url='https://osu.ppy.sh/u/{}'.format(user['user_id']))
        em.set_thumbnail(url='https://a.ppy.sh/{}?{}'.format(user['user_id'], time.perf_counter()))
        em.set_footer(text='Joined')
        em.timestamp = joined
        return em

    async def process_nochoke(self, user):
        await self.checkrequests()
        scores = await get_user_best(self.jamubot.settings['key'], user, 0, 100)
        for i in range(len(scores)):
            btmap = await self.bm_check(scores[i]['beatmap_id'])
            scores[i]['count300'] = str(int(scores[i]['count300']) + int(scores[i]['countmiss']))
            scores[i]['countmiss'] = 0
            scores[i]['maxcombo'] = btmap.max_combo()
            pp, _, _ = await self.get_pyttanko(btmap, int(scores[i]['enabled_mods']), scores[i]['count300'], scores[i]['count100'], scores[i]['count50'], scores[i]['countmiss'], scores[i]['maxcombo'])
            scores[i]['pp'] = pp
            scores[i]['number'] = i
        nochokescores = sorted(scores, key=operator.itemgetter('pp'), reverse=True)
        return nochokescores

    async def process_scores(self, user, mode, juststats=None):
        await self.checkrequests()
        scores = await get_user_best(self.jamubot.settings['key'], user, mode, 20)
        style, cs, ar, od, bpm, mods = 0, 0, 0, 0, [], {}
        for score in scores:
            btmap = await self.bm_check(score['beatmap_id'])
            pp, nochoke, stars = await self.get_pyttanko(btmap, int(score['enabled_mods']), score['count300'], score['count100'], score['count50'], score['countmiss'], score['maxcombo'])
            cs += btmap.cs
            ar += btmap.ar
            od += btmap.od
            bpm.extend([timing.ms_per_beat for timing in btmap.timing_points if timing.change])
            style += stars.speed / stars.total * 100
            mod = pyttanko.mods_str(int(score['enabled_mods']))
            if mod in mods:
                mods[mod] += 1
            else:
                mods[mod] = 1
        numscores = len(scores)
        speed = style / 20
        aim = 100 - (style / 20)
        cs = cs / numscores
        ar = ar / numscores
        od = od / numscores
        bpm = (sum(bpm) / len(bpm))
        for mod in mods:
            mods[mod] = mods[mod]
        if juststats:
            return (speed, aim, cs, ar, od, bpm, float(scores[0]['pp']), mods)
        stats = "▸ **Streams:** {:.2f}%\n".format(speed)
        stats += "▸ **Jumps:** {:.2f}%\n".format(aim)
        stats += "▸ **Circle Size:** {:.2f}\n".format(cs)
        stats += "▸ **Approach Rate:** {:.2f}\n".format(ar)
        stats += "▸ **BPM:** {:.2f}\n".format(bpm / 2)
        return stats

    # These score embed functions are all basically the same however
    # I'm not quite willing to make a dynamic function to make the code shorter
    # I like having an extent of control over how each individual format
    # Looks, so I'll keep it as such unless I decide it needs less code
    async def scores_embed(self, user, scores, gamemode, modenum, recent=None):
        await self.checkrequests()
        user = await get_user(self.jamubot.settings['key'], user, modenum)
        info = ""
        for i, score in enumerate(scores):
            num = i if not recent else score['number']
            btmap = await self.bm_check(score['beatmap_id'])
            acc = pyttanko.acc_calc(int(score['count300']), int(score['count100']), int(score['count50']), int(score['countmiss']))
            # Keeping this line in case pyoppai bindings become available for oppai-ng
            #oppai = await get_pyoppai('beatmaps/{}.osu'.format(score['beatmap_id']), int(score['enabled_mods']), acc, int(score['countmiss']), int(score['maxcombo']))
            pp, nochoke, stars = await self.get_pyttanko(btmap, int(score['enabled_mods']), score['count300'], score['count100'], score['count50'], score['countmiss'], score['maxcombo'])
            info += "**{}: [{}[{}]]({}) +{}**\n".format(num + 1, btmap.title.replace('*', '\*'), btmap.version.replace('*', '\*'), 'https://osu.ppy.sh/b/{}'.format(score['beatmap_id']), pyttanko.mods_str(int(score['enabled_mods'])))
            info += "    ▸ **{:.2f}PP  {}/{}  {:.2f}%**\n".format(pp, score['maxcombo'], btmap.max_combo(), acc * 100)
            info += "      ▸  **{}  {}/{}/{}/{}  {:.2f}★**\n".format(score['score'], score['count300'], score['count100'], score['count50'], score['countmiss'], stars.total)
            info += "        ▸ {}*ago*\n".format(await time_ago(datetime.utcnow(), datetime.strptime(score['date'], '%Y-%m-%d %H:%M:%S')))
            if int(score['maxcombo']) < btmap.max_combo():
                info += '        ▸ **{:.2f}PP For {:.2f}% Perfect FC**\n'.format(nochoke, pyttanko.acc_calc(int(score['count300']) + int(score['countmiss']), int(score['count100']), int(score['count50']), 0) * 100)
        em = discord.Embed(description=info, colour=0x00FFC0)
        if info == "":
            em.set_author(name="No plays found for {}".format(user[0]['username']), icon_url='https://a.ppy.sh/{}?{}'.format(user[0]['user_id'], time.perf_counter()), url='https://osu.ppy.sh/users/{}'.format(user[0]['user_id']))
        else:
            em.set_author(name="{} {} Plays for {}".format('Recent' if recent == 'recent' else 'Nochoke' if recent == 'nochoke' else 'Best', gamemode, user[0]['username']), icon_url='https://a.ppy.sh/{}?{}'.format(user[0]['user_id'], time.perf_counter()), url='https://osu.ppy.sh/users/{}'.format(user[0]['user_id']))
        return em

    async def map_scores_embed(self, user, scores, gamemode, modenum, mapid):
        await self.checkrequests()        
        user = await get_user(self.jamubot.settings['key'], user, modenum)
        btmap = await self.bm_check(mapid)
        info = "**[{}[{}]]({})**\n".format(btmap.title.replace('*', '\*'), btmap.version.replace('*', '\*'), 'https://osu.ppy.sh/b/{}'.format(mapid))
        for i, score in enumerate(scores):
            acc = pyttanko.acc_calc(int(score['count300']), int(score['count100']), int(score['count50']), int(score['countmiss']))
            # Keeping this line in case pyoppai bindings become available for oppai-ng
            #oppai = await get_pyoppai('beatmaps/{}.osu'.format(mapid), int(score['enabled_mods']), acc, int(score['countmiss']), int(score['maxcombo']))
            pp, nochoke, stars = await self.get_pyttanko(btmap, int(score['enabled_mods']), score['count300'], score['count100'], score['count50'], score['countmiss'], score['maxcombo'])
            info += "  ▸ **+{}  {:.2f}PP  {}/{}  {:.2f}%**\n".format(pyttanko.mods_str(int(score['enabled_mods'])), pp, score['maxcombo'], btmap.max_combo(), acc * 100)
            info += "    ▸  **{}  {}/{}/{}/{}  {:.2f}★**\n".format(score['score'], score['count300'], score['count100'], score['count50'], score['countmiss'], stars.total)
            info += "      ▸ {}*ago*\n".format(await time_ago(datetime.utcnow(), datetime.strptime(score['date'], '%Y-%m-%d %H:%M:%S')))
            if int(score['maxcombo']) < btmap.max_combo():
                info += '        ▸ **{:.2f}PP For {:.2f}% Perfect FC**\n'.format(nochoke, pyttanko.acc_calc(int(score['count300']) + int(score['countmiss']), int(score['count100']), int(score['count50']), 0) * 100)
        em = discord.Embed(description=info, colour=0x00FFC0)
        if scores == []:
            em.set_author(name="No plays found for {}".format(user[0]['username']), icon_url='https://a.ppy.sh/{}?{}'.format(user[0]['user_id'], time.perf_counter()), url='https://osu.ppy.sh/users/{}'.format(user[0]['user_id']))
        else:
            em.set_author(name="Best {} Plays for {}".format(gamemode, user[0]['username']), icon_url='https://a.ppy.sh/{}?{}'.format(user[0]['user_id'], time.perf_counter()), url='https://osu.ppy.sh/users/{}'.format(user[0]['user_id']))
        return em

    async def score_embed(self, user, score, scorenum, gamemode, modenum):
        await self.checkrequests()        
        user = await get_user(self.jamubot.settings['key'], user, modenum)
        info = ""
        btmap = await self.bm_check(score['beatmap_id'])
        acc = pyttanko.acc_calc(int(score['count300']), int(score['count100']), int(score['count50']), int(score['countmiss']))
        # Keeping this line in case pyoppai bindings become available for oppai-ng
        #oppai = await get_pyoppai('beatmaps/{}.osu'.format(score['beatmap_id']), int(score['enabled_mods']), acc, int(score['countmiss']), int(score['maxcombo']))
        pp, nochoke, stars = await self.get_pyttanko(btmap, int(score['enabled_mods']), score['count300'], score['count100'], score['count50'], score['countmiss'], score['maxcombo'])
        info += "**{}: [{}[{}]]({}) +{}**\n".format(scorenum, btmap.title.replace('*', '\*'), btmap.version.replace('*', '\*'), 'https://osu.ppy.sh/b/{}'.format(score['beatmap_id']), pyttanko.mods_str(int(score['enabled_mods'])))
        info += "    ▸ **{:.2f}PP  {}/{}  {:.2f}%**\n".format(pp, score['maxcombo'], btmap.max_combo(), acc * 100)
        info += "      ▸  **{}  {}/{}/{}/{}  {:.2f}★**\n".format(score['score'], score['count300'], score['count100'], score['count50'], score['countmiss'], stars.total)
        info += "        ▸ {}*ago*\n".format(await time_ago(datetime.utcnow(), datetime.strptime(score['date'], '%Y-%m-%d %H:%M:%S')))    
        if int(score['maxcombo']) < btmap.max_combo():
            info += '        ▸ **{:.2f}PP For {:.2f}% Perfect FC**\n'.format(nochoke, pyttanko.acc_calc(int(score['count300']) + int(score['countmiss']), int(score['count100']), int(score['count50']), 0) * 100)
        em = discord.Embed(description=info, colour=0x00FFC0)
        if info == "":
            em.set_author(name="No scores found for {}".format(user[0]['username']), icon_url='https://a.ppy.sh/{}?{}'.format(user[0]['user_id'], time.perf_counter()), url='https://osu.ppy.sh/users/{}'.format(user[0]['user_id']))
        else:
            em.set_author(name="Best {} Play for {}".format(gamemode, user[0]['username']), icon_url='https://a.ppy.sh/{}?{}'.format(user[0]['user_id'], time.perf_counter()), url='https://osu.ppy.sh/users/{}'.format(user[0]['user_id']))
        return em

    async def recent_embed(self, user, recent, gamemode, modenum, number):
        await self.checkrequests()
        user = await get_user(self.jamubot.settings['key'], user, modenum)
        info = ""
        for score in recent[:number]:
            btmap = await self.bm_check(score['beatmap_id'])
            acc = pyttanko.acc_calc(int(score['count300']), int(score['count100']), int(score['count50']), int(score['countmiss']))
            # Keeping this line in case pyoppai bindings become available for oppai-ng
            #oppai = await get_pyoppai('beatmaps/{}.osu'.format(score['beatmap_id']), int(score['enabled_mods']), acc, int(score['countmiss']), int(score['maxcombo']))
            pp, nochoke, stars = await self.get_pyttanko(btmap, int(score['enabled_mods']), score['count300'], score['count100'], score['count50'], score['countmiss'], score['maxcombo'])
            info += "**[{}[{}]]({}) +{} {}**\n".format(btmap.title.replace('*', '\*'), btmap.version.replace('*', '\*'), 'https://osu.ppy.sh/b/{}'.format(score['beatmap_id']), pyttanko.mods_str(int(score['enabled_mods'])), score['rank'])
            if score['rank'] != 'F':
                info += "    ▸ **{:.2f}PP  {}/{}  {:.2f}%**\n".format(pp, score['maxcombo'], btmap.max_combo(), acc * 100)
            else: info += "    ▸ **~~{:.2f}PP~~  {}/{}  {:.2f}%**\n".format(pp, score['maxcombo'], btmap.max_combo(), acc * 100)
            info += "      ▸  **{}  {}/{}/{}/{}  {:.2f}★**\n".format(score['score'], score['count300'], score['count100'], score['count50'], score['countmiss'], stars.total)
            info += "        ▸ {}*ago*\n".format(await time_ago(datetime.utcnow(), datetime.strptime(score['date'], '%Y-%m-%d %H:%M:%S')))
            if score['rank'] == 'F':
                info += '          ▸ **{:.2f}%** Complete\n'.format(await self.recent_percent(btmap.hitobjects, score))
            elif int(score['maxcombo']) < btmap.max_combo():
                info += '          ▸ **{:.2f}PP For {:.2f}% Perfect FC**\n'.format(nochoke, pyttanko.acc_calc(int(score['count300']) + int(score['countmiss']), int(score['count100']), int(score['count50']), 0) * 100)
        em = discord.Embed(description=info, colour=0x00FFC0)
        if len(recent) == 0:
            em.set_author(name="No Recent {} Plays for {}".format(gamemode, user[0]['username']), icon_url='https://a.ppy.sh/{}?{}'.format(user[0]['user_id'], time.perf_counter()), url='https://osu.ppy.sh/users/{}'.format(user[0]['user_id']))
        else:
            em.set_author(name="Recent {} Plays for {}".format(gamemode, user[0]['username']), icon_url='https://a.ppy.sh/{}?{}'.format(user[0]['user_id'], time.perf_counter()), url='https://osu.ppy.sh/users/{}'.format(user[0]['user_id']))
        return em

    async def map_embed(self, message, mapid, idtype, modstr='nomod', rec=None):
        if idtype == 'b':
            await self.checkrequests()
            mapset = await get_beatmap(self.jamubot.settings['key'], mapid)
        if idtype == 's':
            await self.checkrequests()
            mapset = await get_beatmapset(self.jamubot.settings['key'], mapid)
        info  = "***Downloads: "
        info += "[map](https://osu.ppy.sh/beatmapsets/{}/download)".format(mapset[0]['beatmapset_id'])
        info += "([no vid](https://osu.ppy.sh/beatmapsets/{}/download?noVideo=1)) ".format(mapset[0]['beatmapset_id'])
        info += " [osu!direct](osu://b/{}) ".format(mapset[0]['beatmap_id'])
        info += " [bloodcat](https://bloodcat.com/osu/s/{})***\n".format(mapset[0]['beatmapset_id'])
        info += "--------------------\n"
        for i in range(len(mapset)): mapset[i]['difficultyrating'] = float(mapset[i]['difficultyrating'])
        mapset = sorted(mapset, key=operator.itemgetter('difficultyrating'), reverse=True)
        for amap in mapset[:5]:
            bmap = await self.bm_check(amap['beatmap_id'])
            info += await self.diff_embed(bmap, amap, modstr, rec)
        em = discord.Embed(description=info, colour=0x00FFC0)
        author = "{} - {} by {}".format(bmap.artist, bmap.title, bmap.creator) if not rec else "{} - {}[{}] by {}".format(bmap.artist, bmap.title, bmap.version, bmap.creator)
        em.set_author(name=author, url="https://osu.ppy.sh/beatmapsets/{}".format(mapset[0]['beatmapset_id']))
        if idtype == 'b':
            graphurl = await self.graph_strains(await self.bm_check(mapset[0]['beatmap_id']), pyttanko.mods_from_str(modstr), mapset[0]['beatmap_id'])
            em.set_image(url=graphurl)
        await message.channel.send(embed=em)

    async def diff_embed(self, bmap, amap, modstr, rec):
        info = "**[[{}]](https://osu.ppy.sh/beatmapsets/{}):**\n".format(bmap.version, amap['beatmapset_id']) if not rec else ''
        diffmod = '' if not rec else ('+No Mod ' if modstr == 'nomod' else '+{} '.format(modstr))
        mods = pyttanko.mods_from_str(modstr)
        accs, ppaccs = [98, 99, 100], {}
        speed_mult, ar, cs, od, _ = pyttanko.mods_apply(mods, bmap.ar, bmap.cs, bmap.od)
        for acc in accs:
            n300, n100, n50 = pyttanko.acc_round(acc, len(bmap.hitobjects), 0)
            ppaccs[str(acc)] = await self.get_pyttanko(bmap, mods=mods, n300=n300, n100=n100, n50=n50, nmiss=0, combo=bmap.max_combo())
        mins, secs, bpm = await self.calc_time(amap, modstr.upper())
        info += "  ▸ **{}Stars:** {:.2f}★ **Length:** {}:{} **Max Combo:** {}\n".format(diffmod, ppaccs[str(acc)][2].total, mins, secs, bmap.max_combo())
        info += "    ▸ **BPM:** {} **AR:** {} **OD:** {} **CS:** {}\n".format(int(bpm), round(ar, 1), round(od, 1), round(cs, 1))
        info += "      ▸ **98%** {:.2f}PP **99%** {:.2f}PP **100%** {:.2f}PP\n".format(ppaccs["98"][0], ppaccs["99"][0], ppaccs["100"][0])
        return info

    async def most_played_embed(self, message, userinfo, maps):
        info = ""
        for mmap in maps:
            bmap = await self.bm_check(mmap['beatmap_id'])
            await self.checkrequests()
            amap = await get_beatmap(self.jamubot.settings['key'], mmap['beatmap_id'])
            info += await self.mp_embed(bmap, mmap, amap[0])
        em = discord.Embed(description=info, colour=0x00FFC0)
        em.set_author(name="{}'s Most Played".format(userinfo['username']), url="https://osu.ppy.sh/users/{}".format(userinfo['user_id']), icon_url='https://a.ppy.sh/{}?{}'.format(userinfo['user_id'], time.perf_counter()))
        await message.channel.send(embed=em)

    async def mp_embed(self, bmap, mmap, amap, mods:int=0):
        info = "**[{}[{}]](https://osu.ppy.sh/beatmapsets/{}):**\n".format(bmap.title.replace('*', '\*'), bmap.version.replace('*', '\*'), amap['beatmapset_id'])
        accs, ppaccs = [98, 99, 100], {}
        speed_mult, ar, cs, od, _ = pyttanko.mods_apply(mods, bmap.ar, bmap.cs, bmap.od)
        for acc in accs:
            n300, n100, n50 = pyttanko.acc_round(acc, len(bmap.hitobjects), 0)
            ppaccs[str(acc)] = await self.get_pyttanko(bmap, mods=mods, n300=n300, n100=n100, n50=n50, nmiss=0, combo=bmap.max_combo())
        mins, secs, bpm = await self.calc_time(amap, '')
        info += "  ▸ **Count:** {} **Stars:** {:.2f}★ **Length:** {}:{}\n".format(mmap['count'], ppaccs[str(acc)][2].total, mins, secs)
        info += "    ▸ **BPM:** {:.2f} **AR:** {} **OD:** {} **CS:** {}\n".format(int(bpm), round(ar, 1), round(od, 1), round(cs, 1))
        info += "      ▸ **98%** {:.2f}PP **99%** {:.2f}PP **100%** {:.2f}PP\n".format(ppaccs["98"][0], ppaccs["99"][0], ppaccs["100"][0])
        return info

    async def bm_check(self, mapid):
        btmap = 'beatmaps/{}.osu'.format(mapid)
        if os.path.exists(btmap): os.remove(btmap)
        await self.download_file('https://osu.ppy.sh/osu/{}'.format(mapid), 'beatmaps/{}.osu'.format(mapid))
        return pyttanko.parser().map(open(btmap))

    async def calc_time(self, amap, mods):
        timefactor = 4/3 if 'DT' in mods else 2/3 if 'HT' in mods else 1
        bpmfactor = 3/2 if 'DT' in mods else 3/4 if 'HT' in mods else 1
        mins, secs = divmod(round(int(amap['total_length']) / timefactor), 60)
        bpm = round(float(amap['bpm']) * bpmfactor)
        return (mins, str(secs).zfill(2), bpm)

    async def download_file(self, url, filename):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                with open(filename, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                return await response.release()

    async def get_web(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.text()

    async def get_pyttanko(self, bmap, mods:int, n300:int, n100:int, n50:int, nmiss:int, combo:int):
        #bmap = pyttanko.parser().map(open(btmap_file))
        stars = pyttanko.diff_calc().calc(bmap, mods=mods)
        pp, _, _, _, _ = pyttanko.ppv2(stars.aim, stars.speed, bmap=bmap, mods=int(mods), n300=int(n300), n100=int(n100), n50=int(n50), nmiss=int(nmiss), combo=int(combo))
        nochoke, _, _, _, _ = pyttanko.ppv2(stars.aim, stars.speed, bmap=bmap, mods=int(mods), n300=int(n300) + int(nmiss), n100=int(n100), n50=int(n50), nmiss=0)
        return (pp, nochoke, stars)

    async def mode_to_str(self, mode):
        if   mode == 0: return 'Standard'
        elif mode == 1: return 'Taiko'
        elif mode == 2: return 'CTB'
        elif mode == 3: return 'Mania'
        else:           return 'New Gamemode?'

    # These next two are from my osu-strains script
    async def get_strains(self, bmap, mods:int=0):
        speed, aim, total, times = [], [], [], []
        seek = 0
        while seek <= bmap.hitobjects[-1].time:
            window = []
            for obj in bmap.hitobjects:
                if (obj.time >= seek and obj.time <= seek + 3000):
                    window.append(obj.strains)
            wspeed, waim, wtotal = [], [], []
            for strain in window:
                wspeed.append(strain[0] / 100)
                waim.append(strain[1] / 100)
                wtotal.append(sum(strain) / 100)
            speed.append(sum(wspeed) / max(len(window), 1))
            aim.append(sum(waim) / max(len(window), 1))
            total.append(sum(wtotal) / max(len(window), 1))
            times.append(seek)
            seek += 500
        return speed, aim, total, times

    async def graph_strains(self, bmap, mods:int=0, bmapid:int=0):
        _ = pyttanko.diff_calc().calc(bmap, mods=mods)
        speed, aim, total, times = await self.get_strains(bmap, mods)
        plt.figure(figsize=(10, 5))
        plt.style.use('ggplot')
        plt.plot(times, speed, color='green', label='Speed', linewidth=3.0)
        plt.plot(times, aim, color='red', label='Aim', linewidth=3.0)
        plt.plot(times, total, color='blue', label='Strain', linewidth=3.0)
        plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(plot_time_format))
        plt.ylabel('Strains')
        plt.legend(loc='best')
        plt.tight_layout()
        filename = 'strains/{}-{}.png'.format(bmapid, mods)
        plt.savefig('/var/www/html/' + filename)
        return 'http://198.199.121.145/' + filename

    async def get_rmap(self, style:float=50, nmaps:int=1, pp:float=None, ar:float=9, od:float=8.0, cs:float=4.0, mods=('nomod', 100)):
        c = self.jamubot.database.cursor()
        args = "style <= {} and style >= {}".format(style + 3, style - 3)
        args += " and pp <= {} and pp >= {}".format(pp + 20, pp - 20)
        args += " and ar <= {} and ar >= {}".format(ar + .8, ar - .8)
        args += " and mods = '{}'".format(self.weighted_choice(mods))
        maps = c.execute('SELECT * FROM maps WHERE {}'.format(args)).fetchall()
        recmaps = []
        if nmaps <= 0:
            nmaps = 1
        for _ in range(nmaps):
            recmaps.append(random.choice(maps))
        return (recmaps, len(maps))

    async def get_map(self, style, pp:float):
        c = self.jamubot.database.cursor()
        if style == 'stream':
            args = "style <= 52"
        if style == 'jump':
            args = "style >= 48"
        args += " and pp <= {} and pp >= {}".format(pp + 20, pp - 20)
        maps = c.execute('SELECT * FROM maps WHERE {}'.format(args)).fetchall()
        rmaps = []
        rmaps.append(random.choice(maps))
        return rmaps
    
    async def recent_percent(self, hitobjects, score, gamemode=0):
        offset = hitobjects[0].time
        totaltime = hitobjects[-1].time - offset
        if gamemode == 0 or gamemode == 1 or gamemode == 2:
            totalhits = int(score['count300']) + int(score['count100']) + int(score['count50']) + int(score['countmiss'])
        elif gamemode == 3:
            totalhits = int(score['count300']) + int(score['count100']) + int(score['count50']) + int(score['countmiss']) + int(score['countkatu']) + int(score['countgeki'])
        lasthit = hitobjects[totalhits - 1].time - offset
        return lasthit / totaltime * 100

    async def on_message(self, message):
        if not message.content.startswith(self.jamubot.settings['prefix']):
            ids = re.findall('\/[s|b]\/([0-9]*)(\?m\=[0-9]*)?([\s]*\+[A-Za-z]+)?', message.content)
            usrns = re.findall('\/u(sers)?\/([a-z0-9]*)', message.content)
            for id, modemsg, mods in ids:
                mods = mods.replace('+', '') if mods != '' else 'nomod'
                if '/b/' in id: await self.map_embed(message, id, 'b', mods.upper(), rec=1)
                if '/s/' in id: await self.map_embed(message, id, 's', mods.upper(), rec=1)
            for usrntype, usrn in usrns:
                await self.checkrequests()
                userinfo = await get_user(self.jamubot.settings['key'], usrn.replace('/u/', ''), 0)
                await message.channel.send(embed=await self.profile_embed(userinfo[0], 'Standard'))
            # New osu pages support
            beatmapsets = re.findall('\/beatmapsets\/([0-9]*)\#?([a-z]*)?\/?([0-9]*)?([\s]*\+[A-Za-z]+)?', message.content)
            for mapset, mode, beatmap, mods in beatmapsets:
                mods = mods.replace('+', '') if mods != '' else 'nomod'
                if beatmap == '': await self.map_embed(message, mapset, 's', mods.upper())
                else: await self.map_embed(message, beatmap, 'b', mods.upper(), rec=1)

    async def checkrequests(self):
        self.jamubot.currentrequests += 1
        if self.jamubot.currentrequests > 1000:
            await self.jamubot.get_user(103139260340633600).send('Current Requests hit 1000.')
            await asyncio.sleep(60 - (now() - self.jamubot.lastrequestreset))

def plot_time_format(time, pos=None):
    s, mili = divmod(time, 1000)
    m, s = divmod(s, 60)
    return "%d:%02d" % (m, s)

def setup(bot):
    bot.add_cog(Osu(bot))
