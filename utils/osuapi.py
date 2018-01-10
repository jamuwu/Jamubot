import asyncio
import aiohttp

async def get_beatmap(key, beatmap_id, session=None):
    url = "https://osu.ppy.sh/api/get_beatmaps?k={}&b={}".format(key, beatmap_id)
    return await request(url, session=session)

async def get_beatmap_hash(key, hash, session=None):
    url = "https://osu.ppy.sh/api/get_beatmaps?k={}&h={}".format(key, hash)
    return await request(url, session=session)

async def get_beatmapset(key, set_id, session=None):
    url = "https://osu.ppy.sh/api/get_beatmaps?k={}&s={}".format(key, set_id)
    return await request(url, session=session)

async def get_scores(key, beatmap_id, user, mode, session=None):
    url = "https://osu.ppy.sh/api/get_scores?k={}&u={}&b={}&m={}".format(key, user, beatmap_id, mode)
    return await request(url, session=session)

async def get_user(key, user, mode, session=None):
    url = "https://osu.ppy.sh/api/get_user?k={}&u={}&m={}".format(key, user, mode)
    return await request(url, session=session)

async def get_user_best(key, user, mode, limit, session=None):
    url = "https://osu.ppy.sh/api/get_user_best?k={}&u={}&m={}&limit={}".format(key, user, mode, limit)
    return await request(url, session=session)

async def get_user_recent(key, user, mode, session=None):
    url = "https://osu.ppy.sh/api/get_user_recent?k={}&u={}&m={}".format(key, user, mode)
    return await request(url, session=session)

async def get_most_played(userid, mode, session=None):
    url = "https://osu.ppy.sh/users/{}/beatmapsets/most_played".format(userid)
    return await request(url, session=session)

async def fixsession():
    async with aiohttp.ClientSession() as session:
        return session

async def request(url, session=None):
    if not session:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()
    else:
        async with session.get(url) as resp:
            return await resp.json()