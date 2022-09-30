import discord
from discord.ext import commands
from utils.db import Database
## TODO: Clean the code, add more comments, and add more features, make it much more user friendly

class Snippet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.group()
    @commands.guild_only()
    async def snippet(self, ctx):
        if ctx.invoked_subcommand is None:
          embed = discord.Embed(title="Help", description="```\nsnippet set [name] ['text']\nsnippet use [name]```", color=0x00ff00)
          await ctx.send(embed=embed)

    @snippet.command()
    async def set(self, ctx):
     stuff = {}
     await ctx.send("Please enter the name of the tag")
     def check(m):
        return m.content and m.channel

     msg = await self.bot.wait_for("message", check=check, timeout=60)
     if not msg:
        await ctx.send("No message found")
        return
     stuff.update({"command": msg.content.lower()})
     def check_text(m):
        return m.content and m.channel
     await ctx.send("Please enter what this tag will say.")
     msg_tag = await self.bot.wait_for("message", check=check_text, timeout=60)
     if not msg_tag:
        await ctx.send("No message found")
        return
     stuff.update({"text": msg_tag.content})
     def check_embed(m):
         return m.content and m.channel
     await ctx.send("Is this a embed? (yes/no)")
     msg_embed = await self.bot.wait_for("message", check=check_embed, timeout=60)
     if not msg_embed:
         await ctx.send("No message found")
         return
     if msg_embed.content.lower() == "yes":
         stuff.update({"embed": True})
     elif msg_embed.content.lower() == "no":
      pass
     await self.db.create_command(ctx.guild.id, stuff)
     print(stuff)
     await ctx.send("Tag set successfully.")

    @snippet.command()
    async def use(self, ctx, name):
         stuff = await self.db.find_command(ctx.guild.id, name)
         data = await self.db.find_ticket_user(ctx.channel.id)
         user = await self.bot.fetch_user(data["_id"])
         if stuff:
               if stuff["embed"]:
                  embed = discord.Embed(title="Ticket Reply", description=stuff["text"], color=0x00ff00)
                  await user.send(embed=embed)
                  # send webhook
                  webhook = await ctx.channel.webhooks()  # type: ignore
                  await webhook[0].send(stuff["text"], username=ctx.author.name, avatar_url=ctx.author.avatar.url) # type: ignore
               else:
                  await user.send(stuff["text"])
                  webhook = await ctx.channel.webhooks()  # type: ignore
                  await webhook[0].send(stuff["text"], username=ctx.author.name, avatar_url=ctx.author.avatar.url) # type: ignore
         else:
               await ctx.send("This tag does not exist.")
            

async def setup(bot):
    await bot.add_cog(Snippet(bot))