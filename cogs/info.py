import discord
import pygit2
import itertools
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

from discord.ext import commands
from utils.bot import ModMail
from typing import Union
import requests

def format_commit(commit: pygit2.Commit) -> str:
    # CREDITS: https://github.com/Rapptz/RoboDanny
    short, _, _ = commit.message.partition('\n')
    short_sha2 = commit.hex[0:6]
    commit_tz = datetime.timezone(datetime.timedelta(minutes=commit.commit_time_offset))
    commit_time = datetime.datetime.fromtimestamp(
        commit.commit_time).astimezone(commit_tz)

    offset = f'<t:{int(commit_time.astimezone(datetime.timezone.utc).timestamp())}:R>'
    return f'[`{short_sha2}`](https://github.com/DeveloperJosh/ModMail/commit/{commit.hex}) {short} ({offset})'


def get_commits(count: int = 3):
    # CREDITS: https://github.com/Rapptz/RoboDanny
    repo = pygit2.Repository('.git')
    commits = list(itertools.islice(repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), count))
    return '\n'.join(format_commit(commit) for commit in commits)


class Info(commands.Cog):
     def __init__(self, bot: ModMail):
            self.bot = bot

     @commands.hybrid_command(name="botinfo", help="Get some info about me!")
     async def botinfo(self, ctx):
        embed = discord.Embed(
            title=f" Info about me!",
            description="Modern modmail for modern Discord servers.",
            color=0x00ff00,
            timestamp=datetime.datetime.utcnow()
        ).add_field(
            name="Stats:",
            value=f"""
**Servers:** {len(self.bot.guilds)}
**Users:** {len(self.bot.users)}
**Commands:** {len(self.bot.commands)}
            """,
            inline=True
        ).add_field(
            name="Links:",
            value=f"""
- [Support Server](https://discord.gg/TeSHENet9M)
- [Github](https://github.com/DeveloperJosh/ModMail)
- [Invite](https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands)
            """,
            inline=True
        ).set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url
        ).set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url
        ).set_thumbnail(url=self.bot.user.display_avatar.url)
        try:
            embed.add_field(
                name="Latest Commits:",
                value=get_commits(),
                inline=False
            )
        except Exception:
            pass
        await ctx.reply(embed=embed)

     @commands.hybrid_command(name="invite", help="Invite me to your server!")
     async def invite(self, ctx):
        await ctx.reply(embed=discord.Embed(
            title="🔗 Click me to invite!",
            description="""
Other links:
- [Support Server](https://discord.gg/TeSHENet9M)
- [Github](https://github.com/DeveloperJosh/ModMail)
                    """,
            url=f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=1879174385&scope=bot%20applications.commands",
            color=0x00ff00
        ).set_footer(text="Thank you very much! 💖"))

     @commands.hybrid_command(name="vote", help="Vote for the bot!")
     async def vote(self, ctx):
        embed = discord.Embed(
        title="Vote for me!",
        description=f" Thank you very much! 💖, [Vote here](https://top.gg/bot/781639675868872796/vote)",
        color=0x00ff00
        ).set_footer(text="Thank you very much! 💖")
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))