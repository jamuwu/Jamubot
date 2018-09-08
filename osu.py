import aiohttp, discord
from discord.ext import commands
from utils.embeds import user_embed
from utils.api import TooManyApiRequests, ApiUnreachable, PPPlusError
import time


class Osu:
    '''Osu commands for all'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def osu(self, ctx, *usernames):
        if len(usernames) == 0:
            row = await self.bot.db.fetchrow(
                f'SELECT * FROM users WHERE discordid = {ctx.author.id}')
            if not row:
                await ctx.send('No user provided.')
                return
            usernames = (row['username'], )
        print(usernames)
        for username in usernames:
            try:
                user = await self.bot.api.get_user(username, 0)
                try:
                    # If this fails, ignore and move on
                    pppuser = await self.bot.api.get_ppp(username)
                except PPPlusError:
                    pppuser = None
                except ApiUnreachable:
                    pppuser = None
            except TooManyApiRequests:
                await ctx.send(
                    f'I\'ve made too many requests to the Osu! api. Please wait {(self.bot.api.last_reset + 60) - time.time()} seconds before using this command again!'
                )
                return
            except ApiUnreachable:
                await ctx.send('The osu! api is not responding.')
                return
            em = user_embed(user, pppuser['user_data'])
            await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Osu(bot))