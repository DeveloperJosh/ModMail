import discord
from discord.ext import commands 
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.emojis = True
intents.emojis_and_stickers = True
intents.bans = True

bot = commands.Bot(
    activity=discord.Game(name="Dm me for help!"),
    command_prefix="!",
    intents=intents,
    case_insensitive=True,
    allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True, replied_user=True),
    strip_after_prefix=True,
    help_command=None
)


async def load_cogs():
    i = 0
    files = os.listdir('./cogs')
    for file in files:
        if file.endswith('.py'):
            await bot.load_extension(f'cogs.{file[:-3]}')
            i += 1
    print(f'{i} cogs loaded')

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("DISCORD_TOKEN"), reconnect=True)  # type: ignore
    
@bot.event
async def on_ready():
    # clear the console
    # os.system('cls' if os.name == 'nt' else 'clear')
    print("""

   _____                             __ _     __  __           _                 _ _ 
 / ____|                           / _| |   |  \/  |         | |               (_) |
| (___  _   _ _ __   ___ _ __ __ _| |_| |_  | \  / | ___   __| |_ __ ___   __ _ _| |
 \___ \| | | | '_ \ / __| '__/ _` |  _| __| | |\/| |/ _ \ / _` | '_ ` _ \ / _` | | |
 ____) | |_| | | | | (__| | | (_| | | | |_  | |  | | (_) | (_| | | | | | | (_| | | |
|_____/ \__, |_| |_|\___|_|  \__,_|_|  \__| |_|  |_|\___/ \__,_|_| |_| |_|\__,_|_|_|
         __/ |                                                                      
        |___/                                                                       

""") 
    print(f"Logged in as {bot.user}")
    print(f"Connected to: {len(bot.guilds)} guilds")
    print(f"Connected to: {len(bot.users)} users")
    print(f"Connected to: {len(bot.cogs)} cogs")
    print(f"Connected to: {len(bot.commands)} commands")
    print(f"Connected to: {len(bot.emojis)} emojis")
    print(f"Connected to: {len(bot.voice_clients)} voice clients")
    print(f"Connected to: {len(bot.private_channels)} private_channels")