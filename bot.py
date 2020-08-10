from dataclasses import dataclass
from discord import Status, Game
from discord.ext import commands
from utils.api import Api
import asyncio, asyncpg
import ujson, os


@dataclass
class Config:
  dtoken: str
  prefix: str
  dbuser: str
  dbpass: str
  dbname: str
  dbhost: str


class Bot(commands.AutoShardedBot):
  def __init__(self):
    with open('config.json') as f:
      self.config = Config(**ujson.loads(f.read()))
    self.api = Api(self)
    custom = Game(name='with a new rewrite')
    super().__init__(self.config.prefix, status=Status.dnd, activity=custom)

  async def run(self):
    self.load_extension('osu')
    await super().start(self.config.dtoken)

  async def __aenter__(self):
    self.db = await asyncpg.connect(
      user=self.config.dbuser,
      password=self.config.dbpass,
      database=self.config.dbname,
      host=self.config.dbhost
    )
    await self.api.load()
    return self

  async def __aexit__(self, *args):
    await self.api.close()
    await self.db.close()

  async def on_ready(self):
    print(f'Logged in as {self.user}')


async def main():
  async with Bot() as bot:
    await bot.run()

if __name__ == '__main__':
  if os.name == 'nt':
    os.system('SET PGCLIENTENCODING=utf-8')
    os.system('chcp 65001')
  asyncio.run(main())