from typing import Dict
import discord
from utils.db import Database
from discord.ext import commands, tasks
from utils.embed import custom_embed, error_embed, success_embed, image_embed

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.Cog.listener('on_command')
    async def cmd_logs(self, ctx):
        if not ctx.guild:
            return
        channel = self.bot.get_channel(889112702146986024)
        await channel.send(embed=discord.Embed(
            title="Command used:",
            # show if command was context or slash
            description=f"Command: {ctx.command}",
            #description=f"Command: `{ctx.message.content if isinstance(ctx, commands.Context) else ctx.command.name}`",
            color=discord.Color.blurple()
        ).set_author(name=f"{ctx.author} | {ctx.author.id}", icon_url=ctx.author.display_avatar.url
        ).add_field(name="Channel:", value=f"{ctx.channel.mention}\n#{ctx.channel.name} ({ctx.channel.id})"
        ).add_field(name="Guild:", value=f"{ctx.guild.name}\n{ctx.guild.id}"))

    @commands.Cog.listener('on_guild_join')
    async def on_guild_join(self, guild: discord.Guild):
        text_to_send = f"""
Hey there! Thanks a lot for inviting me!
If you are a server admin then please run `{self.bot.command_prefix}setup` or `/setup` this server.
If you face any issues, feel free to join our support server:
- https://discord.gg/TeSHENet9M
"""

        log_embed = discord.Embed(
            title="New guild joined",
            description=f"{guild.name} ({guild.id})",
            color=discord.Color.blurple()
        ).set_author(name=f"{guild.owner}", icon_url=guild.owner.display_avatar.url # type: ignore
        ).add_field(name="Humans:", value=f"{len(list(filter(lambda m: not m.bot, guild.members)))}"
        ).add_field(name="Bots:", value=f"{len(list(filter(lambda m: m.bot, guild.members)))}"
        ).set_footer(text=f"Owner ID: {guild.owner_id}")
        if guild.icon is not None:
            log_embed.set_thumbnail(url=guild.icon.url)

        await self.bot.get_channel(889116736077570068).send(embed=log_embed)

        for channel in guild.channels:
            if "general" in channel.name:
                try:
                    return await channel.send(text_to_send)  # type: ignore
                except Exception:
                    pass

        for channel in guild.channels:
            if "bot" in channel.name or "cmd" in channel.name or "command" in channel.name:
                try:
                    return await channel.send(text_to_send)  # type: ignore
                except Exception:
                    pass

        for channel in guild.channels:
            try:
                return await channel.send(text_to_send)  # type: ignore
            except Exception:
                pass

    @commands.Cog.listener('on_guild_remove')
    async def on_guild_remove(self, guild: discord.Guild):
        log_embed = discord.Embed(
            title="Guild left",
            description=f"{guild.name} ({guild.id})",
            color=discord.Color.red()
        ).set_author(name=f"{guild.owner}", icon_url=guild.owner.display_avatar.url # type: ignore
        ).add_field(name="Humans:", value=f"{len(list(filter(lambda m: not m.bot, guild.members)))}"
        ).add_field(name="Bots:", value=f"{len(list(filter(lambda m: m.bot, guild.members)))}"
        ).set_footer(text=f"Owner ID: {guild.owner_id}")
        if guild.icon is not None:
            log_embed.set_thumbnail(url=guild.icon.url)

        await self.bot.get_channel(889116736077570068).send(embed=log_embed)
    
    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def block(self, ctx, id: str):
        try:
            if await self.db.is_blocked(id):
                embed = error_embed("Error", "This user is already blocked")
                return await ctx.send(embed=embed)
            else:
                await self.db.block(id)
                embed = success_embed("Success", "This user has been blocked")
                return await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)
            print(e)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def unblock(self, ctx, id):
        try:
            if await self.db.is_blocked(id):
                await self.db.unblock(id)
                embed = success_embed("Success", "This user has been unblocked")
                return await ctx.send(embed=embed)
            else:
                embed = error_embed("Error", "This user is not blocked")
                return await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)
            print(e)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def users(self, ctx):
      users = await self.db.get_users()
      embed = custom_embed("Users", f"Total Users: {len(users)}")
      for user in users:
            embed.add_field(name=user["_id"], value=user["ticket"], inline=False)
      await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension):
     try:
      await self.bot.reload_extension(f"cogs.{extension}")
      await self.bot.tree.sync()
      embed = discord.Embed(title='Reload', description=f'{extension} successfully reloaded', color=0xff00c8)
      await ctx.send(embed=embed)
     except Exception as e:
        print(e)
        embed = discord.Embed(title='Reload', description=f'{extension} could not be reloaded', color=0xff0000)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension):
     await self.bot.reload_extension(f"cogs.{extension}")
     embed = discord.Embed(title='loaded', description=f'{extension} successfully loaded', color=0xff00c8)
     await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def set_game(self, ctx, *, game):
     await self.bot.change_presence(activity=discord.Game(name=game))
     embed = discord.Embed(title='Game', description=f'Game set to {game}', color=0xff00c8)
     await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def debug(self, ctx, *, mode):
        if mode == 'on':
         self.bot.debug = True
         embed = discord.Embed(title='Debug', description=f'Debug mode is now on', color=0xff00c8)
         await ctx.send(embed=embed)
        elif mode == 'off':
         self.bot.debug = False
         embed = discord.Embed(title='Debug', description=f'Debug mode is now off', color=0xff00c8)
         await ctx.send(embed=embed)
        else:
         embed = discord.Embed(title='Debug', description=f'Invalid mode', color=0xff00c8)
         await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Developer(bot))