import asyncio, aiohttp, asyncpg, discord
from discord.ext import commands
import json, logging, logging.config
from utils.api import Api

logging.basicConfig(filename='log.log', level=logging.INFO)
logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        with open('config.json') as f:
            self.dict = json.loads(f.read())

    def __getitem__(self, x):
        return self.dict[x]

    def __getattr__(self, x):
        return self.dict[x]


class Bot(commands.AutoShardedBot):
    def __init__(self):
        self.config = Config()
        super().__init__(self.config.prefix)

    async def run(self):
        await super().start(self.config.token)

    async def __aenter__(self):
        self.db = await asyncpg.connect(
            user='postgres',
            password=self.config.dbpass,
            database=self.config.dbname)
        self.session = aiohttp.ClientSession()
        self.api = Api(self)
        return self

    async def __aexit__(self, *args):
        await self.db.close()
        await self.session.close()
        await super().logout()

    async def on_ready(self):
        for cog in self.config.cogs:
            try:
                self.load_extension(f'{cog}')
            except Exception as e:
                print(f'Failed to load cog.{cog}')
                print(f'{type(e).__name__}: {e}')
        print(f'Logged in as {self.user}')


async def main():
    async with Bot() as bot:
        await bot.run()


asyncio.run(main())