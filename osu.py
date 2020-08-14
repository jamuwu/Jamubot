from discord.ext import commands

class Osu(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_message(self, msg):
    if not msg.author.bot:
      print(msg)

  @commands.command()
  async def setuser(self, ctx, *, username):
    '''Sets your osu username'''
    if (oid:= await self.bot.api.id_from_str(username)):
      if await self.bot.db.fetchrow('SELECT oid FROM users WHERE did=$1', ctx.author.id):
        await self.bot.db.execute('UPDATE users SET oid=$1 WHERE did=$2', oid, ctx.author.id)
      else:
        await self.bot.db.execute('INSERT INTO users(oid, did) VALUES($1, $2)', oid, ctx.author.id)
      await ctx.send(f'Set username to {username}')
    else:
      await ctx.send(f'User not found')

  @commands.command(aliases=['taiko', 'fruits', 'mania'])
  async def osu(self, ctx, *, username=None):
    '''Gets osu user info'''
    alias = ctx.message.clean_content.split(' ')[0].replace(ctx.prefix, '')
    if not username:
      if (r:= await self.bot.db.fetchrow('SELECT oid FROM users WHERE did=$1', ctx.author.id)):
        username = r['oid']
      else:
        res = f'Usage: `{ctx.prefix}osu [username]`\n'
        res += f'Or run `{ctx.prefix}setuser [username]`'
        return await ctx.send(res)
    user = await self.bot.api.user(username, alias)
    if 'error' in user:
      return await ctx.send(f'User not found')
    await ctx.send(embed=user.as_embed)

  @commands.command(aliases=['rs'])
  async def recent(self, ctx, *, username=None):
    '''Gets recent score info'''
    if not username:
      if (r:= await self.bot.db.fetchrow('SELECT oid FROM users WHERE did=$1', ctx.author.id)):
        oid = r['oid']
      else:
        res = f'Usage: `{ctx.prefix}recent [username]`\n'
        res += f'Or run `{ctx.prefix}setuser [username]`'
        return await ctx.send(res)
    else:
      oid = await self.bot.api.id_from_str(username)
    score = await self.bot.api.recent(oid)
    if 'error' in score or len(score) == 0:
      return await ctx.send('No recent scores found')
    if await self.bot.db.execute('SELECT mid FROM maphistory WHERE chan=$1', ctx.channel.id):
      await self.bot.db.execute('UPDATE maphistory SET mid=$1 WHERE chan=$2', score[0]['beatmap']['id'], ctx.channel.id)
    else:
      await self.bot.db.execute('INSERT INTO maphistory ($1, $2)', score[0]['beatmap']['id'], ctx.channel.id)
    await ctx.send(embed=score[0].as_embed)

  @commands.command()
  async def top(self, ctx, *, username=None):
    '''Gets best score info'''
    if not username:
      if (r:= await self.bot.db.fetchrow('SELECT oid FROM users WHERE did=$1', ctx.author.id)):
        oid = r['oid']
      else:
        res = f'Usage: `{ctx.prefix}top [username]`\n'
        res += f'Or run `{ctx.prefix}setuser [username]`'
        return await ctx.send(res)
    else:
      oid = await self.bot.api.id_from_str(username)
    scores = await self.bot.api.best(oid)
    if 'error' in scores or len(scores) == 0:
      return await ctx.send('No scores found')
    if await self.bot.db.fetchrow('SELECT mid FROM maphistory WHERE chan=$1', ctx.channel.id):
      await self.bot.db.execute('UPDATE maphistory SET mid=$1 WHERE chan=$2', scores[0]['beatmap']['id'], ctx.channel.id)
    else:
      await self.bot.db.execute('INSERT INTO maphistory(chan, mid) VALUES($1, $2)', scores[0]['beatmap']['id'], ctx.channel.id)
    await ctx.send(embed=scores.as_embed)

  #@comamnds.command(aliases=['c'])
  #async def compare(self, ctx, *, username=None):
    #'''Compare your top plays on the last map sent by the bot'''
    # TODO figure out how to make this work on api v2


def setup(bot):
  bot.add_cog(Osu(bot))