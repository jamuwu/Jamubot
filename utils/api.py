import asyncio
import aiohttp
from time import time

from cachetools import cachedasync, TTLCache
cache = TTLCache(100, 300)


class TooManyApiRequests(Exception):
    pass


class ApiUnreachable(Exception):
    pass


class PPPlusError(Exception):
    pass


class Api:
    def __init__(self, bot, **kwargs):
        self.bot = bot
        self.current = 0
        self.last_reset = time()

        self.limit = int(kwargs.get('limit', 1000))
        self.base = kwargs.get('base', 'https://osu.ppy.sh/api/')

    def check_requests(self, limit):
        if not limit: return True
        if time() <= self.last_reset + 60:
            self.current += 1
        else:
            self.current = 0
            self.last_reset = time()
        return self.current <= self.limit

    async def fetch(self, url, limit=True):
        if self.check_requests(limit):
            async with self.bot.session.get(url) as resp:
                if 'application/json' not in resp.headers['content-type']:
                    raise ApiUnreachable
                if await resp.read() == b'error': raise PPPlusError
                return await resp.json()
        else:
            raise TooManyApiRequests

    @cachedasync(cache)
    async def get_ppp(self, username):
        url = f'https://syrin.me/pp+/api/user/{username}'
        return await self.fetch(url, False)

    async def get_beatmap(self, beatmap_id):
        url = f'{self.base}get_beatmaps?k={self.bot.config.key}&b={beatmap_id}'
        return await self.fetch(url)

    async def get_beatmap_hash(self, hash):
        url = f'{self.base}get_beatmaps?k={self.bot.config.key}&h={hash}'
        return await self.fetch(url)

    async def get_beatmapset(self, set_id):
        url = f'{self.base}get_beatmaps?k={self.bot.config.key}&s={set_id}'
        return await self.fetch(url)

    async def get_scores(self, beatmap_id, user, mode):
        url = f'{self.base}get_scores?k={self.bot.config.key}&u={user}&b={beatmap_id}&m={mode}'
        return await self.fetch(url)

    async def get_user(self, user, mode):
        url = f'{self.base}get_user?k={self.bot.config.key}&u={user}&m={mode}'
        return (await self.fetch(url))[0]

    async def get_user_best(self, user, mode, limit):
        url = f'{self.base}get_user_best?k={self.bot.config.key}&u={user}&m={mode}&limit={limit}'
        return await self.fetch(url)

    async def get_user_recent(self, user, mode, limit):
        url = f'{self.base}get_user_recent?k={self.bot.config.key}&u={user}&m={mode}&limit={limit}'
        return await self.fetch(url)

    async def get_most_played(self, userid):
        url = f'https://osu.ppy.sh/users/{userid}/beatmapsets/most_played'
        return await self.fetch(url)
