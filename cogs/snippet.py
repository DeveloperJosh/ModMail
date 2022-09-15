import discord
from discord.ext import commands
from utils.db import Database

class Snippet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.group(invoke_without_command=False)
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
     await self.db.create_command(ctx.guild.id, stuff)
     await ctx.send("Tag set successfully.")

    @snippet.command()
    async def use(self, ctx, name):
        name = name.lower()
        if name is None:
            await ctx.send("Please enter a command name.")
        else:
           try:
            command = await self.db.find_command(ctx.guild.id, name)
            text = command["text"]  # type: ignore
            id = ctx.channel.name.split("-")[1]  # type: ignore
            user = self.bot.get_user(int(id))
            embed = discord.Embed(title="Ticket Reply", description=f"**{text}**", color=0x00ff00)
            embed.set_footer(text=f"Server: {ctx.guild.name}")
            webhook = await ctx.channel.webhooks()  # type: ignore
            await webhook[0].send(text, username=ctx.author.name, avatar_url=ctx.author.avatar.url) # type: ignore
            await user.send(embed=embed)
           except Exception as e:
            await ctx.send(e)
            print(e)

async def setup(bot):
    await bot.add_cog(Snippet(bot))