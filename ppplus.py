import aiohttp, discord
from discord.ext import commands
from utils.embeds import ppplus_embed
from utils.api import ApiUnreachable, TooManyApiRequests, PPPlusError
import time


class PPPlus:
    '''PP+ Stats (Thanks Syrin)'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['pp+'])
    async def ppplus(self, ctx, *username):
        if len(username) == 0:
            row = await self.bot.db.fetchrow(
                f'SELECT * FROM users WHERE discordid = {ctx.author.id}')
            if not row:
                await ctx.send('No user provided.')
                return
            username = row['username']
        else:
            username = ' '.join(list(username))
        try:
            user = await self.bot.api.get_ppp(username)
            em = ppplus_embed(user['user_data'])
            await ctx.send(embed=em)
        except PPPlusError:
            await ctx.send(
                'Syrin.me returned an error. This most likely means the user couldn\'t be found.'
            )
        except ApiUnreachable:
            await ctx.send(
                'Syrin.me is unreachable at the moment, please try again in 5 minutes.'
            )


def setup(bot):
    bot.add_cog(PPPlus(bot))