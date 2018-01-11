from datetime import datetime, timedelta
from time import perf_counter as now
from collections import defaultdict
from discord.ext import commands
from string import ascii_letters
from operator import itemgetter
from utils.dataIO import dataIO
from utils.osuapi import *
from utils import pyttanko
from random import choice
import os, json, re
import traceback
import sqlite3
import discord
import asyncio
import aiohttp
import logging

class Tracker:
    def __init__(self, bot):
        self.bot = bot
        self.players = dataIO.load_json("track.json")
        self.buffer = {}
        self.tracktime = []
        self.avgreq = []
        loop = asyncio.get_event_loop()
        loop.create_task(self.resetrequests())
        loop.create_task(self.tracker())

    @commands.group()
    async def track(self, ctx):
        if ctx.invoked_subcommand is None:
            helpmsg  = '```\n~track\n\n'
            helpmsg += 'Commands:\n'
            helpmsg += '  add    Adds players to tracking list.\n'
            helpmsg += '  remove Removes players from the tracking list.\n'
            helpmsg += '  list   Shows a list of the tracked players.\n'
            helpmsg += '  time   Sends the average amount of time for track loops.```'
            await ctx.message.channel.send(helpmsg)
            return

    @track.command(no_pm=True)
    async def add(self, ctx, *usernames):
        """Adds players to tracking list."""
        if ctx.message.author.guild_permissions.manage_guild == False and ctx.message.author.id not in self.bot.settings['devs']:
            await ctx.message.channel.send("Sorry friend, but you can only do this if you have the 'Manage Server' permission. {}".format(self.bot.emotes['bingCry']))
            return
        message = await ctx.message.channel.send('Processing...')
        messages = ""
        added, already, notadded = 0, 0, 0
        for username in usernames:
            await self.checkrequests()
            data = await get_user(self.bot.settings['key'], username, 0)
            if data == []:
                notadded += 1
                messages += '`{}` Not found.\n'.format(username)
                continue
            data = data[0]
            if data['username'].lower() in self.players:
                if ctx.message.channel.id not in self.players[data['username'].lower()]['channels']:
                    self.players[data['username'].lower()]['channels'].append(ctx.message.channel.id)
                    messages += '`{}` Successfully added.\n'.format(data['username'])
                    added += 1
                else:
                    messages += '`{}` Already being tracked.\n'.format(data['username'])
                    already += 1
            else:
                user = {
                    'last_check': str(datetime.utcnow() + timedelta(hours=8)),
                    'channels': [ctx.message.channel.id],
                    'data': data
                }
                self.players[data['username'].lower()] = user
                messages += '`{}` Successfully added.\n'.format(data['username'])
                added += 1
        if len(list(usernames)) > 10:
            messages = ""
            messages += "Added `{}` to the tracking list\n".format(added) if added != 0 else ''
            messages += "`{}` Are alreaady being tracked\n".format(already) if already != 0 else ''
            messages += "Unable to add `{}`".format(notadded) if notadded != 0 else ''
        await message.edit(content=messages)

    @track.command(no_pm=True)
    async def remove(self, ctx, *usernames):
        """Removes players from the tracking list."""
        if ctx.message.author.guild_permissions.manage_guild == False and ctx.message.author.id not in self.bot.settings['devs']:
            await ctx.message.channel.send("Sorry friend, but you can only do this if you have the 'Manage Server' permission. {}".format(self.bot.emotes['bingCry']))
            return
        message = await ctx.message.channel.send('Processing...')
        messages = ""
        removed, notremoved = 0, 0
        for username in usernames:
            if username.lower() in self.players:
                if ctx.message.channel.id in self.players[username.lower()]['channels']:
                    self.players[username.lower()]['channels'].remove(ctx.message.channel.id)
                    messages += 'Successfully removed `{}`.\n'.format(username)
                    removed += 1
                    await self.checkforemptytrack(username)
                else:
                    messages += '`{}` Not being tracked here.\n'.format(username)
                    notremoved += 1
            else:
                messages += '`{}` Not being tracked here.\n'.format(username)
                notremoved += 1
        if len(list(usernames)) > 10:
            messages = ""
            messages += "Removed `{}` from the tracking list\n".format(removed) if removed != 0 else ''
            messages += "`{}` Weren't being tracked here".format(notremoved) if notremoved != 0 else ''
        await message.edit(content=messages)

    @track.command(name="list", )
    async def _list(self, ctx):
        userlist = [self.players[u]['data'] for u in self.players if ctx.message.channel.id in self.players[u]['channels']]
        for i in range(len(userlist)): userlist[i]['pp_rank'] = int(userlist[i]['pp_rank'])
        userlist = sorted(userlist, key=itemgetter('pp_rank'))
        info = ''
        for user in userlist: info += '[{}: #{} {}PP](https://osu.ppy.sh/u/{})\n'.format(
            user['username'], user['pp_rank'], user['pp_raw'], user['user_id'])
        if len(userlist) == 0:
            em = discord.Embed(title='No users currently tracked in #{}'.format(ctx.message.channel.name), color=0x00FFC0)
        elif len(info) >= 2000:
            info = info[:2000].split('\n')[:-2]
            info.append('{} More...'.format(len(userlist) - len(info)))
            info = '\n'.join(info)
            em = discord.Embed(title='{} Users currently tracked in #{}'.format(len(userlist), ctx.message.channel.name), description=info, color=0x00FFC0)
        else:
            em = discord.Embed(title='Users currently tracked in #{}'.format(ctx.message.channel.name), description=info[:1900], color=0x00FFC0)
        await ctx.message.channel.send(embed=em)

    @track.command(name="time", )
    async def _time(self, ctx):
        average = round(sum(self.tracktime) / max(len(self.tracktime), 1), 2)
        await ctx.message.channel.send('Average time to complete a tracking loop: {} Seconds'.format(average))

    @track.command(name="avgrequests", )
    async def _requests(self, ctx):
        average = round(sum(self.avgreq) / max(len(self.avgreq), 1), 2)
        await ctx.message.channel.send('Average requests to the osu api per minute: {}'.format(int(average)))

    @commands.command(hidden=True)
    async def testevent(self, ctx, username='cookiezi'):
        data = await get_user(self.bot.settings['key'], username, 0)
        data = data[0]
        user = {
            'username': username,
            'channels': [ctx.message.channel.id],
            'data': data,
            'last_check': str(datetime.utcnow() + timedelta(hours=8))
        }
        for event in user['data']['events']:
            em = await self.parse_event(event, user['username'], datetime.strptime(event['date'], '%Y-%m-%d %H:%M:%S'))
            if em: await ctx.message.channel.send(embed=em)

    async def new_score(self, old, new, score, channels, timestamp, rank=''):
        em = await self.score_embed(old, new, score, timestamp, rank)
        for channel in channels:
            if channel == 0: # Lol, this is for something else
                async with aiohttp.ClientSession() as session:
                    await session.post('urlhere')
                return
            else:
                try: await self.bot.get_channel(int(channel)).send(embed=em)
                except: await self.bot.get_user(103139260340633600).send("Error in the tracking loop:\n{}".format(traceback.format_exc()))

    async def new_event(self, user, event, channels, timestamp):
        try: em = await self.parse_event(event, user, timestamp)
        except IndexError: em = None
        if em:
            for channel in channels:
                if channel == 0: # Lol, this is for something else
                    async with aiohttp.ClientSession() as session:
                        await session.post('urlhere')
                    return
                else:
                    try: await self.bot.get_channel(int(channel)).send(embed=em)
                    except: await self.bot.get_user(103139260340633600).send("Error in the tracking loop:\n{}".format(traceback.format_exc()))
    
    async def update(self):
        for olduser in self.buffer.keys():
            if olduser in self.players:
                self.players[olduser]['data'] = self.buffer[olduser]['data']
                self.players[olduser]['last_check'] = self.buffer[olduser]['last_check']    
        dataIO.save_json("track.json", self.players)
        return True

    async def resetrequests(self):
        while self == self.bot.get_cog("Tracker"):
            self.avgreq.append(self.bot.currentrequests)
            self.avgreq = self.avgreq[-20:]
            self.bot.currentrequests = 0
            self.bot.lastrequestreset = now()
            await asyncio.sleep(60)

    async def checkrequests(self):
        self.bot.currentrequests += 1
        if self.bot.currentrequests >= 1000:
            await self.bot.get_user(103139260340633600).send('Current Requests hit 1000.')
            await asyncio.sleep(60 - (now() - self.bot.lastrequestreset))

    async def tracker(self):
        maxrequests = 1000
        while self == self.bot.get_cog("Tracker"):
            try: # Eating excepts and sending them to myself helps a lot with debugging, I hate checking logs
                self.buffer = self.players
                start = now()
                for username in self.buffer.copy():
                    try:
                        async with aiohttp.ClientSession() as session:
                            user = self.buffer[username]
                            if '.' in user['last_check']:
                                last = datetime.strptime(user['last_check'], '%Y-%m-%d %H:%M:%S.%f')
                            else:
                                last = datetime.strptime(user['last_check'], '%Y-%m-%d %H:%M:%S')
                            await self.checkrequests()
                            try: data = await get_user(self.bot.settings['key'], user['data']['user_id'], 0, session=session)
                            except aiohttp.client_exceptions.ClientPayloadError:
                                await self.checkrequests()
                                data = await get_user(self.bot.settings['key'], user['data']['user_id'], 0)
                            if data == []: continue
                            data = data[0]
                            curbmaps = {}
                            data['events'].reverse()
                            for event in data['events']:
                                then = datetime.strptime(event['date'], '%Y-%m-%d %H:%M:%S')
                                difference = last - then
                                if difference.total_seconds() <= 0.0:
                                    if 'achieved' in event['display_html'] and '(osu!)' in event['display_html']: 
                                        if user['data']['pp_raw'] != data['pp_raw']:
                                            bmapid = re.findall('\/b\/[0-9]*', event['display_html'])[0].replace('/b/', '')
                                            rank = re.findall('\#[0-9]*', event['display_html'])[0]
                                            curbmaps[str(bmapid)] = rank
                                        else:
                                            try: await self.new_event(user['data'], event, user['channels'], then)
                                            except OverflowError: await self.bot.get_user(103139260340633600).send("Overflowerror again.\nEvent is: {}".format(event))
                                    else: 
                                        try: await self.new_event(user['data'], event, user['channels'], then)
                                        except OverflowError: await self.bot.get_user(103139260340633600).send("Overflowerror again.\nEvent is: {}".format(event))
                            if user['data']['pp_raw'] != data['pp_raw']:
                                await self.checkrequests()
                                try: scores = await get_user_best(self.bot.settings['key'], user['data']['user_id'], 0, 100, session=session)
                                except aiohttp.client_exceptions.ClientPayloadError:
                                    await self.checkrequests()
                                    scores = await get_user_best(self.bot.settings['key'], user['data']['user_id'], 0, 100)
                                scorenum = 0
                                for i in range(len(scores)):
                                    score = scores[i]
                                    scorenum += 1
                                    score['number'] = scorenum
                                    then = datetime.strptime(score['date'], '%Y-%m-%d %H:%M:%S')
                                    difference = last - then
                                    if difference.total_seconds() <= 0.0:
                                        rank = curbmaps[score['beatmap_id']] if score['beatmap_id'] in curbmaps else ''
                                        try: await self.new_score(user['data'], data, score, user['channels'], then, rank)
                                        except OverflowError: await self.bot.get_user(103139260340633600).send("Overflowerror again.\nEvent is: {}".format(event))
                            if data['username'].lower() not in self.buffer:
                                self.buffer[data['username'].lower()] = self.buffer[username]
                                self.buffer.pop(username)
                            self.buffer[data['username'].lower()]['last_check'] = str(datetime.utcnow() + timedelta(hours=8))
                            # The idea of this is to let me use it later, and also prevent rank decay from showing when they get a new score
                            # In other words I want new top score notifications to show the raw ranks gained and the raw pp gained
                            self.buffer[data['username'].lower()]['data'] = data 
                        await self.update()
                    except: await self.bot.get_user(103139260340633600).send("Error in the tracking loop:\n{}".format(traceback.format_exc()))
                self.tracktime.append(now() - start)
                self.tracktime = self.tracktime[-6:]
            except: await self.bot.get_user(103139260340633600).send("Error in the tracking loop:\n{}".format(traceback.format_exc()))

    async def parse_event(self, event, user, timestamp):
        info, title, disp, username = '', '', event['display_html'], user['username']
        """Might eventually use this to show more events
                1 - #40-1,000 place score (any gamemode)
                1 - Map deleted
                2 - Beatmap update
                2 - First place lost
                2 - osu!supporter tag
                2 - #10-39 place score
                4 - Username change
                4 - Beatmap submission
                4 - Achievement unlocked
                4 - #1-9 place score (any gamemode)
                5 - Beatmap revived from graveyard
                8 - Beatmap ranked/qualified
                8 - Map played X times
                8 - First place (osu!standard only) on a beatmap with >=250(?) scores"""
        if 'achieved' in disp and '(osu!)' in disp:
            # 1-39 on a map, specifically standard for now
            rank = re.findall('\#[0-9]*', disp)[0]
            if int(rank.replace('#', '')) > max(int(user['pp_rank']) / 10, 10): return None
            mapid = int(event['beatmap_id'])
            bmap = await self.bm_check(mapid)
            title = "{} has achieved {} on".format(username, rank)
            await self.checkrequests()
            score = await get_scores(self.bot.settings['key'], mapid, username, 0)
            info += await self.eventscore(score[0], mapid)
        elif 'has lost first place' in disp:
            mapid = int(event['beatmap_id'])
            bmap = await self.bm_check(mapid)
            info += "**{} has lost first place on [{}[{}]](https://osu.ppy.sh/b/{})**".format(username, bmap.title, bmap.version, mapid)
        elif 'changed their username' in disp:
            info = "**Username change: {} ▸ {}**".format("#Todo", "#Eventually")
        elif 'unlocked the medal' in disp and 'medal!' in disp:
            medal = re.findall('"\<b\>[^\<]*\<\/b\>"', disp)[0].replace('<b>', '').replace('</b>', '')
            info = "**{} has unlocked the {} achievement!**".format(username, medal)
        elif 'has submitted a new beatmap' in disp: # The problem with this is that I can't tell what mode it is, this will create errors if I try displaying map info if it's not standard
            mapset = int(event['beatmapset_id'])
            mapname = re.findall('\>[^<]*<\/a\>\"', disp)[0].replace('>', '').replace('</a"', '')
            info  = "**{} has submitted [{}](https://osu.ppy.sh/beatmapsets/{})**".format(username, mapname, mapset)
        elif 'has updated the beatmap' in disp: # Same as above
            mapset = int(event['beatmapset_id'])
            mapname = re.findall('\>[^<]*<\/a\>\"', disp)[0].replace('>', '').replace('</a"', '')
            info = "**{} has updated [{}](https://osu.ppy.sh/beatmapsets/{})**".format(username, mapname, mapset)
        elif 'has just been qualified' in disp: # Yes even more
            mapset = int(event['beatmapset_id'])
            mapname = re.findall('\>[^<]*<\/a\>', disp)[0].replace('>', '').replace('</a', '')
            info = "**{}'s map [{}](https://osu.ppy.sh/beatmapsets/{}) has been qualified**".format(username, mapname, mapset)
        elif 'has been revived from eternal slumber' in disp: # You guessed it! Same.
            mapset = int(event['beatmapset_id'])
            mapname = re.findall('\>[^<]*<\/a\>', disp)[0].replace('>', '').replace('</a', '')
            info = "**{} has revived [{}](https://osu.ppy.sh/beatmapsets/{})**".format(username, mapname, mapset)
        else: return None
        if info == '': return None
        em = discord.Embed(title=title, description=info, color=0x00FFC0)
        em.timestamp = timestamp - timedelta(hours=8)
        return em

    async def eventscore(self, score, mapid):
        info = ""
        btmap = await self.bm_check(mapid)
        acc = pyttanko.acc_calc(int(score['count300']), int(score['count100']), int(score['count50']), int(score['countmiss']))
        # Keeping this line in case pyoppai bindings become available for oppai-ng
        #oppai = await get_pyoppai('beatmaps/{}.osu'.format(score['beatmap_id']), int(score['enabled_mods']), acc, int(score['countmiss']), int(score['maxcombo']))
        pp, nochoke, stars = await self.get_pyttanko(btmap, int(score['enabled_mods']), score['count300'], score['count100'], score['count50'], score['countmiss'], score['maxcombo'])
        info += "**[{}[{}]]({}) +{}**\n".format(btmap.title.replace('*', '\*'), btmap.version.replace('*', '\*'), 'https://osu.ppy.sh/b/{}'.format(mapid), pyttanko.mods_str(int(score['enabled_mods'])))
        info += "    ▸ **{:.2f}PP  {}/{}  {:.2f}%**\n".format(pp, score['maxcombo'], btmap.max_combo(), acc * 100)
        info += "      ▸  **{}  {}/{}/{}/{}  {:.2f}★**\n".format(score['score'], score['count300'], score['count100'], score['count50'], score['countmiss'], stars.total)
        if int(score['maxcombo']) < btmap.max_combo():
            info += '        ▸ **{:.2f}PP For {:.2f}% Perfect FC**\n'.format(nochoke, pyttanko.acc_calc(int(score['count300']) + int(score['countmiss']), int(score['count100']), int(score['count50']), 0) * 100)
        return info

    async def score_embed(self, old, new, score, timestamp, rank):
        info = ""
        btmap = await self.bm_check(score['beatmap_id'])
        acc = pyttanko.acc_calc(int(score['count300']), int(score['count100']), int(score['count50']), int(score['countmiss']))
        # Keeping this line in case pyoppai bindings become available for oppai-ng
        #oppai = await get_pyoppai('beatmaps/{}.osu'.format(score['beatmap_id']), int(score['enabled_mods']), acc, int(score['countmiss']), int(score['maxcombo']))
        pp, nochoke, stars = await self.get_pyttanko(btmap, int(score['enabled_mods']), score['count300'], score['count100'], score['count50'], score['countmiss'], score['maxcombo'])
        info += "**[{}[{}]]({}) +{} {}**\n".format(btmap.title.replace('*', '\*'), btmap.version.replace('*', '\*'), 'https://osu.ppy.sh/b/{}'.format(score['beatmap_id']), pyttanko.mods_str(int(score['enabled_mods'])), rank)
        info += "    ▸ **{:.2f}PP  {}/{}  {:.2f}%**\n".format(pp, score['maxcombo'], btmap.max_combo(), acc * 100)
        info += "      ▸  **{}  {}/{}/{}/{}  {:.2f}★**\n".format(score['score'], score['count300'], score['count100'], score['count50'], score['countmiss'], stars.total)
        if int(score['maxcombo']) < btmap.max_combo():
            info += '        ▸ **{:.2f}PP For {:.2f}% Perfect FC**\n'.format(nochoke, pyttanko.acc_calc(int(score['count300']) + int(score['countmiss']), int(score['count100']), int(score['count50']), 0) * 100)
        oldpp,   newpp   = float(old['pp_raw']), float(new['pp_raw'])
        oldrank, newrank =   int(old['pp_rank']),  int(new['pp_rank'])
        em = discord.Embed(description=info, colour=0x00FFC0)
        em.set_author(name="New #{} for {} (+{:.2f}PP {}{} Ranks)".format(score['number'], new['username'], newpp - oldpp, '+' if oldrank - newrank >= 0 else '', oldrank - newrank), 
                      icon_url='https://a.ppy.sh/{}'.format(new['user_id']), url='https://osu.ppy.sh/u/{}'.format(new['user_id']))
        em.timestamp = timestamp - timedelta(hours=8)
        return em

    async def checkforemptytrack(self, username):
        if username in self.players[username]:
            if len(self.players[username]['channels']) == 0:
                self.players.pop(username)

    async def bm_check(self, mapid):
        btmap = 'beatmaps/{}.osu'.format(mapid)
        if os.path.exists(btmap): os.remove(btmap)
        await self.download_file('https://osu.ppy.sh/osu/{}'.format(mapid), 'beatmaps/{}.osu'.format(mapid))
        try: return pyttanko.parser().map(open(btmap))
        except: print(btmap)

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

    async def get_pyttanko(self, bmap, mods:int, n300:int, n100:int, n50:int, nmiss:int, combo:int):
        #bmap = pyttanko.parser().map(open(btmap_file))
        stars = pyttanko.diff_calc().calc(bmap, mods=mods)
        pp, _, _, _, _ = pyttanko.ppv2(stars.aim, stars.speed, bmap=bmap, mods=int(mods), n300=int(n300), n100=int(n100), n50=int(n50), nmiss=int(nmiss), combo=int(combo))
        nochoke, _, _, _, _ = pyttanko.ppv2(stars.aim, stars.speed, bmap=bmap, mods=int(mods), n300=int(n300) + int(nmiss), n100=int(n100), n50=int(n50), nmiss=0)
        return (pp, nochoke, stars)

def setup(bot):
    n = Tracker(bot)
    bot.add_cog(n)