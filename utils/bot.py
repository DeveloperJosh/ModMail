import logging
import logging.handlers
from aiohttp import ClientSession
import os
from dotenv import load_dotenv
import datetime
from .db import Database
db = Database()

load_dotenv()

from typing import Dict, List, Optional

import discord
from discord.ext import commands, tasks

class ModMail(commands.Bot):
    def __init__(
        self,
        *args,
        initial_cogs: List[str],
        client: ClientSession,
        debug: bool = False,
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.client = client
        self.debug = debug
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_cogs
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("discord")
        logger.setLevel(logging.INFO)
        time = datetime.datetime.now()

    async def setup_hook(self) -> None:

        for extension in self.initial_extensions:
            await self.load_extension(f"cogs.{extension}")

        # if debug is enabled, then don't sync slash commands
        if not self.debug:
           try:
            logging.info("Syncing slash commands...")
            await self.tree.sync()
            logging.info("Slash commands synced!")
           except Exception as e:
            logging.error("Failed to sync slash commands.")
            logging.error(e)
        else:
            pass

    async def on_message(self, message):
        if message.author.bot:
            return
        # check debug mode
        devs = [542798185857286144, 321750582912221184]
        if self.debug:
                return
        elif message.author.id in devs:
                await self.process_commands(message)
        else:
            await self.process_commands(message)

async def main():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    intents.emojis = True
    intents.emojis_and_stickers = True
    intents.bans = True
    intents.webhooks = True
    ext = ['modmail', 'errors', 'developer', 'config', 'snippets', 'help', 'info']
    async with ClientSession() as server_client:
     async with ModMail(debug=False, command_prefix="?", allowed_mentions=discord.AllowedMentions(everyone=False, roles=True, users=True, replied_user=True),  activity=discord.Game("DM for support"), owner_ids=[542798185857286144, 321750582912221184], help_command=None, client=server_client, intents=intents, testing_guild_id=884470177176109056, initial_cogs=ext) as bot:
      token = os.getenv("DISCORD_TOKEN")
      await bot.start(f"{token}", reconnect=True)