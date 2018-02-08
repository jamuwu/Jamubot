# -*- coding: utf-8 -*-
from discord.ext import commands
import sys, re, os, time, io
from utils import pyttanko
import asyncio, aiohttp

info  = sys.stdout.write
error = sys.stderr.write

class IRCbot:
    def __init__(self, bot):
        self.bot = bot
        self.nick = self.bot.settings['ircnick'] # ?
        self.passw = self.bot.settings['irctoken'] # ?
        self.buffer = {}
        self.session = aiohttp.ClientSession()
        loop = asyncio.get_event_loop()
        loop.create_task(self.client())

    async def send_message(self, target, msg):
        '''Processes messages to prevent spam'''
        if target not in self.buffer:
            # I guess since this is the first message to this user we can
            # Just send it immediately after adding them to the buffer
            self.buffer[target] = {
                'messages': [], 'timer': time.time(),
                'last_msg': time.time(), 'nb_msg': 1}
            self.send(target, msg)
        else:
            self.buffer[target]['messages'].append(msg)

    async def check_buffer(self): # Is there a way to compress these two into one function, since they're mostly the same?
        '''Processes buffer and sends any messages that are able to be sent now'''
        for target in self.buffer.copy():
            if len(self.buffer[target]['messages']) == 0:
                self.buffer.pop(target)
                continue
            now = time.time() # I'd put this outside the loop, but what if there's a lot of messages :^)
            if now - self.buffer[target]['last_msg'] >= 8:
                self.buffer[target]['timer'] = now
                self.buffer[target]['nb_msg'] = 0
            if now - self.buffer[target]['last_msg'] >= 1 and self.buffer[target]['nb_msg'] <= 5:
                msg = self.buffer[target]['messages'].pop(0)
                self.send(target, msg)
                self.buffer[target]['nb_msg'] += 1
                self.buffer[target]['last_msg'] = now

    def send(self, target, msg):
        '''Sends a private message to the target'''
        self.writer.write(f'PRIVMSG {target} {msg}\n'.encode())
        info(f'To {target}: {msg}\n') # So we can see the messages sent

    def pong(self, msg):
        '''Responds to pings sent by the IRC server'''
        self.writer.write(f'PONG {msg[-1]}\n'.encode())
        # So we know it's still connected during debugging
        info('My heart fluttered.\n')

    async def get_text(self):
        '''Recieve, split, and parse data coming from the irc server'''
        messages = []
        data = await self.reader.read(2048)
        if not data:
            await self.reconnect()
            return messages
        text = data.decode('utf-8')
        for line in text.split('\n'):
            if line.strip() != '':
                parsed = self.parse_line(line)
                if parsed[1] == 'PING': self.pong(parsed)
                # This is so we don't process these, as there are a lot of them
                elif parsed[1] != 'QUIT': messages.append(parsed)
        return messages

    def parse_line(self, line):
        '''Parse lines of data with regex'''
        parsed = re.findall('^(?:[:](\S+) )?(\S+)(?: (?!:)(.+?))?(?: [:](.+))?$', line)
        try: return parsed[0] # Don't judge this, I just want to see why it randomly crashes sometimes xd
        except: info(line); return ('', '', '', '')

    async def connect(self):
        '''Connects and logs into the IRC server'''
        self.reader, self.writer = await asyncio.open_connection('irc.ppy.sh', 6667, ssl=False)
        info('Connected to Bancho.\n')
        self.writer.write(f'USER {self.nick} {self.nick} {self.nick} :Test bot\n'.encode())
        self.writer.write(f'PASS {self.passw}\n'.encode())
        self.writer.write(f'NICK {self.nick}\n'.encode())

    async def reconnect(self):
        '''I'm hoping this makes reconnecting easy'''
        info('Reconnecting...')
        await self.close()
        await self.connect()

    async def close(self):
        '''I guess this is to properly handle closing the connection?'''
        self.writer.close()

    async def get_bmap(self, mapid):
        async with self.session.get(f'https://osu.ppy.sh/osu/{mapid}') as resp:
            return await resp.text()

    async def get_json(self, url):
        async with self.session.get(url) as resp:
            return await resp.json()

    def get_bpm(self, bmap):
        '''Computes the bpm of this beatmap'''
        mpbs = [x.ms_per_beat for x in bmap.timing_points if x.change]
        if len(mpbs) == 0: return 0
        mpb = sum(mpbs) / len(mpbs)
        if (mpb == 0): return 0
        return 60000 / mpb

    def calc_pp_for_acc(self, bmap, stars, accs=[100], mods=0):
        '''Calcs the PP for a list of accs'''
        pps = []
        for acc in accs:
            n300, n100, n50 = pyttanko.acc_round(acc, len(bmap.hitobjects), 0)
            pp, _, _, _, _ = pyttanko.ppv2(stars.aim, stars.speed, bmap=bmap, mods=int(mods), n300=int(n300), n100=int(n100), n50=int(n50), nmiss=0, combo=bmap.max_combo())
            pps.append(pp)
        return pps

    def process_mods(self, msg):
        mods = ''
        if '+Hidden' in msg:         mods += 'HD'
        if '+HardRock' in msg:       mods += 'HR'
        if '+DoubleTime' in msg:     mods += 'DT'
        if '+Nightcore' in msg:      mods += 'NC'
        if '+Flashlight' in msg:     mods += 'FL'
        if '+SuddenDeath' in msg:    mods += 'SD'
        if '+Perfect' in msg:        mods += 'PF'
        if '-Easy' in msg:           mods += 'EZ'
        if '-HalfTime' in msg:       mods += 'HT'
        if '-SpunOut' in msg:        mods += 'SO'
        if '-NoFail' in msg:         mods += 'NF'
        return mods

    async def build_map(self, mapid, modbit=0):
        '''Builds a string to give various infos of a linked map'''
        bmap = pyttanko.parser().map(io.StringIO(await self.get_bmap(mapid)))
        stars = pyttanko.diff_calc().calc(bmap, mods=modbit)
        pp100, pp99, pp98, pp97 = self.calc_pp_for_acc(bmap, stars, [100, 99, 98, 97])
        speed_mult = 1
        mins, secs = divmod((bmap.hitobjects[-1].time / speed_mult) / 1000, 60)
        infos  =  '\x01ACTION'
        infos += f' [https://osu.ppy.sh/b/{mapid}'
        infos += f' {bmap.title}[{bmap.version}] {pyttanko.mods_str(modbit)}]'
        infos += f' ▸ 97%: {round(pp97, 2)} ▸ 98%: {round(pp98, 2)}'
        infos += f' ▸ 99%: {round(pp99, 2)} ▸ 100%: {round(pp100, 2)}'
        infos += f' ▸ {int(mins)}:{int(secs)}♪ ▸ {round(stars.total, 2)}★'
        infos += f' ▸ ~{round(self.get_bpm(bmap), 2)}BPM ▸ AR: {bmap.ar}'
        infos += f' ▸ CS: {bmap.cs} ▸ OD: {bmap.od}'
        infos += f' ▸ HP: {bmap.hp}\x01'
        return infos

    async def build_recent(self, sender):
        '''Shows a user their recent score'''
        recent = await self.get_json(f'https://osu.ppy.sh/api/get_user_recent?k={self.bot.settings["key"]}&u={sender}&limit=1')
        if len(recent) < 1: return "It seems you haven't played any maps in the last 24 hours."
        score = recent[0]
        bmap = pyttanko.parser().map(io.StringIO(await self.get_bmap(f'https://osu.ppy.sh/osu/{score["beatmap_id"]}')))
        n300, n100 = int(score['count300']), int(score['count100'])
        n50, nmiss = int(score['count50']), int(score['countmiss'])
        combo, mods = int(score['maxcombo']), int(score['enabled_mods'])
        stars = pyttanko.diff_calc().calc(bmap, mods=mods)
        acc = pyttanko.acc_calc(n300, n100, n50, nmiss) * 100
        pp, _, _, _, _ = pyttanko.ppv2(stars.aim, stars.speed, bmap=bmap, mods=int(mods), n300=int(n300), n100=int(n100), n50=int(n50), nmiss=int(nmiss), combo=int(combo))
        infos  =  '\x01ACTION'
        infos += f' [https://osu.ppy.sh/b/{score["beatmap_id"]}'
        infos += f' {bmap.title}[{bmap.version}] +{pyttanko.mods_str(mods)}]'
        infos += f' {combo}/{bmap.max_combo()}'
        infos += f' {round(acc, 2)}% {round(pp, 2)}PP'
        infos += f' {n300}/{n100}/{n50}/{nmiss}'
        return infos

    async def client(self):
        await self.connect()
        try: # Might add certain handlers for these in the future
            while self == self.bot.get_cog('IRCbot'):
                for msg in await self.get_text():
                    if msg[1] == 'PRIVMSG':
                        sender = msg[0].split('!')[0]
                        command = msg[3].split(' ')[0]
                        info(f'From {sender}: {msg[3]}\n')
                        await self.bot.get_user(103139260340633600).send(f'From {sender}: {msg[3]}')
                        if command == '~recent':
                            await self.send_message(sender, await self.build_recent(sender))
                        elif command == '~user':
                            await self.send_message(sender, 'This is a #TODO')
                        else: # No commands so check for maps
                            for mapid in re.findall('https://osu.ppy.sh/b/([0-9]*)', msg[3]):
                                mods = self.process_mods(msg[3])
                                await self.send_message(sender, await self.build_map(mapid, mods))
                    elif msg[1] in ['001', '372', '375', '376']:
                        info(f'{msg[3].strip()}\n')
                    elif msg[1] in ['311', '319', '312', '318', '401']:
                        info(f'Whois {msg[2].split(" ")[1]}: {msg[3].strip()}\n')
                    elif msg[1] == '464':
                        error('Bad authentication token.\n')
                    else: info(str(msg)) # So we can see if we aren't parsing something we need to be
                await self.check_buffer()
            else: await self.close()
        except KeyboardInterrupt:
            await self.close()
    
    @commands.command(hidden=True)
    async def ircsend(self, ctx, target, *, msg):
        if ctx.message.author.id == 103139260340633600:
            target = target.replace(' ', '_') # I'm too lazy to do that myself while typing
            await self.send_message(target, msg)

    @commands.command(hidden=True)
    async def ircraw(self, ctx, *, raw):
        if ctx.message.author.id == 103139260340633600:
            self.writer.write(f'{raw}\n'.encode())

def setup(bot):
    bot.add_cog(IRCbot(bot))