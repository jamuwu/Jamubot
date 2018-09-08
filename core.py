from discord.ext import commands
import time


class Core:
    '''The base bot functionality'''

    def __init__(self, bot):
        self.bot = bot
        self.up = time.time()

    @commands.command()
    async def uptime(self, ctx):
        await ctx.send(f'Bot has been up for {time.time() - self.up} seconds!')

    @commands.command()
    async def reload(self, ctx, cog):
        self.bot.unload_extension(cog)
        try:
            self.bot.load_extension(cog)
            await ctx.send(f'Reloaded cog.{cog}')
        except Exception as e:
            info = f'Failed to load cog.{cog}\n'
            info += f'```{type(e).__name__}: {e}```'
            await ctx.send(info)


def setup(bot):
    bot.add_cog(Core(bot))