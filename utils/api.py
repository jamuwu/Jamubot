import httpx, ujson, time, os
from oppadc import OsuMap
from .classes import *

class Api:
  def __init__(self, bot):
    self.bot = bot
    self.session = httpx.AsyncClient()
  
  async def load(self):
    r = await self.bot.db.fetchrow('SELECT token, expire FROM api')
    self.token = r['token']
    self.expire = r['expire']
    if time.time() > self.expire:
      await self.refresh()

  async def check(self):
    r = await self.bot.db.fetchrow('SELECT expire FROM api')
    if time.time() > r[0]:
      await self.refresh()
  
  async def refresh(self):
    r = await self.bot.db.fetchrow('SELECT refresh, client_id, client_secret FROM api')
    d = {
      "grant_type": "refresh_token",
      "client_id": r['client_id'],
      "client_secret": r['client_secret'],
      "refresh_token": r['refresh']
    }
    res = await self.session.post('https://osu.ppy.sh/oauth/token', data=d)
    res = ujson.loads(res.text)
    self.token = res['access_token']
    await self.bot.db.execute(
      'UPDATE api SET token=$1, refresh=$2, expire=$3',
      self.token,
      res['refresh_token'],
      time.time() + res['expires_in']
    )

  async def id_from_str(self, s):
    if not (r:= await self.bot.db.fetchrow('SELECT id FROM idcache WHERE name=$1', s.lower())):
      u = await self.user(s)
      if 'error' in u:
        return None
      oid = u['id']
      if not await self.bot.db.fetchrow('SELECT name FROM idcache WHERE id=$1', oid):
        await self.bot.db.execute('INSERT INTO idcache(id, name) VALUES($1, $2)', oid, s.lower())
      else:
        await self.bot.db.execute('UPDATE idcache SET id=$1 WHERE name=$2', oid, s.lower())
    return r['id'] if r else oid

  async def get_bmap(self, r):
    path = f"beatmaps/{r['beatmap']['id']}.osu"
    if not os.path.exists(path):
      m = await self.session.get(f"https://osu.ppy.sh/osu/{r['beatmap']['id']}")
      with open(path, 'a', encoding='utf8') as f:
        for l in m.text.splitlines():
          f.write(f'{l}\n')
    else:
      with open(path, 'r', encoding='utf8') as f:
        m = f.read()
    return OsuMap(file_path=path)

  async def fetch(self, path):
    await self.check()
    r = await self.session.get(f'https://osu.ppy.sh/api/v2/{path}', headers={'Authorization': f'Bearer {self.token}'})
    r = r.json()
    if type(r) == dict:
      if 'beatmap' in r:
        r['bmap'] = await self.get_bmap(r)
    elif type(r) == list:
      for i in range(len(r)):
        if 'beatmap' in r[i]:
          r[i]['bmap'] = await self.get_bmap(r[i])
    return r

  async def user(self, name, mode='osu'):
    u = await self.fetch(f'users/{name}/{mode}')
    return User(u)

  async def recent(self, name, mode='osu'):
    s = await self.fetch(f'users/{name}/scores/recent?include_fails=1&mode={mode}')
    return [Recent(x) for x in s]

  async def best(self, name, mode='osu'):
    s = await self.fetch(f'users/{name}/scores/best?mode={mode}')
    return Best(s[:5])