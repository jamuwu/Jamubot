import aiohttp, discord
import time


class Osu:
    '''Osu commands for all'''

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Osu(bot))