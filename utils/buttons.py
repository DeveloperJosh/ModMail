# buttons
import discord
from discord.ext import commands
from bot import ModMail
from db import Database

class Block_buttons(discord.ui.View):
    """
    Ths is work in progress
    """
    def __init__(self, ctx, bot: ModMail):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.bot = bot
        self.db = Database()

    @discord.ui.button(label="Block", style=discord.ButtonStyle.red)
    async def block(self, b, i):
        await self.db.block(None)
        await self.ctx.send("User has been blocked")
        self.stop()
