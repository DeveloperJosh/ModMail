import discord
from discord.ext import commands
from utils.bot import ModMail

async def get_bot_help(bot: ModMail) -> discord.Embed:
    embed = discord.Embed(
        description="Here are all my commands:",
        color=0x00ff00
    ).set_author(icon_url=bot.user.display_avatar.url, name=f"{bot.user.name}'s Help")
    for cog_name, cog in bot.cogs.items():
        if len(cog.get_commands()) > 0 and cog.qualified_name not in ["Jishaku", "Help", "Developer"]:
            embed.add_field(
                name=cog.qualified_name,
                value='\n'.join(['`' + command.qualified_name + f'` - {command.help}' for command in cog.get_commands()] + ['`/' + command.qualified_name + f'` - {command.description}' for command in cog.walk_app_commands()]),
                inline=False
            )
    embed.add_field(
        name="**Snippets**",
        value="`/snippets add <name> <content>` - Add a snippet\n`/snippets remove <name>` - Remove a snippet\n`/snippets edit <name> <content>` - Edit the text of a snippet\n`/snippets list` - List all snippets",
        inline=False
    )
    return embed.add_field(
        name="‎",
        value=f"[Github](https://github.com/DeveloperJosh/ModMail) | [Support Server](https://discord.gg/TeSHENet9M) | [Vote here](https://top.gg/bot/781639675868872796/vote)",
        inline=False
    ).set_thumbnail(url=bot.user.display_avatar.url)

async def get_cog_help(bot: ModMail, cog: commands.Cog) -> discord.Embed:
    return discord.Embed(
        title=f"{cog.qualified_name} Help",
        description='\n'.join([f"`{bot.command_prefix}{c.qualified_name}{' ' + c.signature if c.signature else ''}` - {c.help}" for c in cog.get_commands()] + [f"`/{c.qualified_name}` - {c.description}" for c in cog.walk_app_commands()]),
        color=0x00ff00
    ).add_field(
        name="‎",
        value=f"[Github](https://github.com/DeveloperJosh/ModMail) | [Support Server](https://discord.gg/TeSHENet9M) | [Vote here](https://top.gg/bot/781639675868872796/vote)",
        inline=False
    )


async def get_command_help(bot, c: commands.Command) -> discord.Embed:
    return discord.Embed(
        title=f"{c.qualified_name.title()} Help",
        description=c.help,
        color=0x00ff00
    ).add_field(name="Usage:", value=f"```{bot.command_prefix}{c.qualified_name}{' ' + c.signature if c.signature else ''}```").add_field(
        name="‎",
        value=f"[Github](https://github.com/DeveloperJosh/ModMail) | [Support Server](https://discord.gg/TeSHENet9M) | [Vote here](https://top.gg/bot/781639675868872796/vote)",
        inline=False
    )


class Help(commands.Cog):
    def __init__(self, bot: ModMail):
        self.bot = bot

    @commands.hybrid_command(name="help", help="Get some help.")
    async def help(self, ctx: commands.Context, command: str = None):
        if command is None:
            return await ctx.reply(embed=await get_bot_help(self.bot))
        maybe_cog = self.bot.get_cog(command.lower().title())
        if maybe_cog is not None:
            return await ctx.reply(embed=await get_cog_help(self.bot, maybe_cog))
        maybe_command = self.bot.get_command(command.lower())
        if maybe_command is not None:
            return await ctx.reply(embed=await get_command_help(self.bot, maybe_command))
        return await ctx.reply(f"No command named `{command}` found.")


async def setup(bot: ModMail):
    await bot.add_cog(Help(bot))