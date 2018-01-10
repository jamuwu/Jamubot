from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from utils.simulation import simulate
from time import perf_counter as time
from utils.parsers import *
from utils.osuapi import *
from utils import pyttanko
import discord, asyncio
import os, sys

class Replay:
    def __init__(self, bot):
        self.bot = bot
    # Attachments look like ['filename', 'height', 'id', 'proxy_url', 'save', 'size', 'url', 'width']
    async def on_message(self, message):
        for attach in message.attachments:
            if '.osr' in attach.filename:
                await self.process_replay(message, attach.id, attach.url)
        for word in message.content.split(' '):
            if word[-4:] == '.osr':
                # I need to try/except this because people are dumb
                try: await self.process_replay(message, message.id, word)
                except: idiotfound = True

    def parse_graph(self, lifegraph):
        data = []
        for hp in lifegraph.split(','):
            if hp != '':
                pos = hp.split('|')
                data.append((float(pos[0]), float(pos[1])))
        return data

    def process_point(self, prevpoint, point, start, end):
        prevx = self.scale_number(prevpoint[0], 0, 400, start, end)
        prevy = self.scale_number(prevpoint[1], 0, 200, 0, 1)
        x = self.scale_number(point[0], 0, 400, start, end)
        y = self.scale_number(point[1], 0, 200, 0, 1)
        return (prevx, 208 - prevy, x, 208 - y)

    def process_event(self, event, start, end):
        x = self.scale_number(event['t'], 0, 400, start, end)
        event['point'] = (x, 2, x, 6)
        if event['event'] == '100':
            event['color'] = (0, 255, 0)
        elif event['event'] == '50':
            event['color'] = (0, 0, 255)
        elif event['event'] == 'miss':
            event['color'] = (255, 0, 0)
        else: event['color'] = (255, 255, 255)
        return event

    def scale_number(self, unscaled, to_min, to_max, from_min, from_max):
        return (to_max-to_min)*(unscaled-from_min)/(from_max-from_min)+to_min

    def process_color(self, point):
        if   point[1] >= .6: return (154, 205, 50)
        elif point[1] <  .6: return (255,   0,  0)

    async def process_replay(self, message, mid, url):
        replayf = await self.get_replay(mid, url)
        replay = parseReplay(replayf)
        bmapf = await self.get_bmap(replay['beatmap_md5'])
        bmap = parse_osu(bmapf)
        # we're done with these files, so let's delete them to save space :D
        os.remove(replayf)
        os.remove(bmapf)
        results = self.generate_graph(replay, bmap)
        em = await self.replay_embed(replay, results)
        await message.channel.send(embed=em)

    def generate_graph(self, replay, bmap):
        results = simulate(bmap[0], bmap[1], replay)
        data = self.parse_graph(replay['life_graph'])
        img = Image.new('RGB', (400, 210))
        draw_img = ImageDraw.Draw(img)
        end = data[-1][0]
        start = data[0][0]
        prevpoint = (start, 1)
        for point in data:
            draw_img.line(self.process_point(prevpoint, point, start, end), width=3, fill=self.process_color(point))
            prevpoint = point
        for event in results['timeline']:
            event = self.process_event(event, start, end)
            draw_img.line(event['point'], fill=event['color'])
        draw_img.line((0, 1, 400, 1))
        draw_img.line((0, 7, 400, 7))
        img.save('/var/www/html/replayfiles/{}.png'.format(replay['replay_md5']))
        return results

    async def replay_embed(self, replay, results):
        info = ""
        acc = pyttanko.acc_calc(int(replay['num_300']), int(replay['num_100']), int(replay['num_50']), int(replay['num_miss']))
        btmap, pp, nochoke, stars = await self.get_pyttanko(replay)
        info += "**{}[{}] +{} {}**\n".format(btmap.title.replace('*', '\*'), btmap.version.replace('*', '\*'), pyttanko.mods_str(int(replay['modbit'])), replay['grade'])
        info += "    ▸ **~~{:.2f}PP~~  {}/{}  {:.2f}%**\n".format(pp, replay['max_combo'], btmap.max_combo(), acc * 100)
        info += "      ▸  **{}  {}/{}/{}/{}  {:.2f}★**\n".format(replay['score'], replay['num_300'], replay['num_100'], replay['num_50'], replay['num_miss'], stars.total)
        if int(replay['max_combo']) < btmap.max_combo():
            info += '        ▸ **{:.2f}PP For {:.2f}% Perfect FC**\n'.format(nochoke, pyttanko.acc_calc(int(replay['num_300']) + int(replay['num_miss']), int(replay['num_100']), int(replay['num_50']), 0) * 100)
        em = discord.Embed(description=info, colour=0x00FFC0)
        em.set_author(name="Replay for {}".format(replay['player']))
        em.set_image(url='http://138.197.225.16/replayfiles/{}.png'.format(replay['replay_md5']))
        return em

    async def get_replay(self, mid, url):
        filename = '/root/replayfiles/{}-{}.osr'.format(mid, time())
        await self.download_file(url, filename)
        return filename

    async def get_bmap(self, md5):
        filename = '/root/replayfiles/{}.osu'.format(md5)
        if not os.path.exists(filename):
            apidata = await get_beatmap_hash(self.bot.settings['key'], md5)
            beatmap_id = apidata[0]['beatmap_id']
            await self.download_file('https://osu.ppy.sh/osu/{}'.format(beatmap_id), filename)
        return filename

    async def get_pyttanko(self, replay):
        mods, n300 = int(replay['modbit']), int(replay['num_300'])
        n100, n50 = int(replay['num_100']), int(replay['num_50'])
        nmiss, combo = int(replay['num_miss']), int(replay['max_combo'])
        bmap = pyttanko.parser().map(open(await self.get_bmap(replay['beatmap_md5'])))
        stars = pyttanko.diff_calc().calc(bmap, mods=mods)
        pp, _, _, _, _ = pyttanko.ppv2(stars.aim, stars.speed, bmap=bmap, mods=mods, n300=n300, n100=n100, n50=n50, nmiss=nmiss, combo=combo)
        nochoke, _, _, _, _ = pyttanko.ppv2(stars.aim, stars.speed, bmap=bmap, mods=mods, n300=n300 + nmiss, n100=n100, n50=n50, nmiss=0)
        return (bmap, pp, nochoke, stars)

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

def setup(bot):
    bot.add_cog(Replay(bot))