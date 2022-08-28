import logging
import logging.handlers
from aiohttp import ClientSession
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

from typing import List, Optional

import discord
from discord.ext import commands

class ModMail(commands.Bot):
    def __init__(
        self,
        *args,
        initial_cogs: List[str],
        client: ClientSession,
        db_pool: asyncpg.Pool,
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.db_pool = db_pool
        self.client = client
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_cogs

    async def setup_hook(self) -> None:

        for extension in self.initial_extensions:
            await self.load_extension(f"cogs.{extension}")

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

async def main():

    logging.basicConfig(level=logging.INFO)
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    intents.emojis = True
    intents.emojis_and_stickers = True
    intents.bans = True
    intents.webhooks = True
    ext = ['modmail', 'errors']                                                           # temp password
    async with ClientSession() as server_client, asyncpg.create_pool(user="blue", password="Gunner0099", host="raspberrypi", port=5432, command_timeout=30) as pool:
     if pool is None:
        print("It looks like the database connecting.")   
        return
     async with ModMail(command_prefix="!", activity=discord.Game("Dm for support"), db_pool=pool, client=server_client, intents=intents, testing_guild_id=884470177176109056, initial_cogs=ext, help_command=None) as bot:
      await bot.start(os.getenv("DISCORD_TOKEN"), reconnect=True)