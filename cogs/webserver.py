import logging
from aiohttp import web
import asyncio
import discord 
from discord.ext import commands
        
class Server(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def start(self):
     async def handler(request):
       return web.Response(text="This api is in the works.")

     app = web.Application()
     app.router.add_get('/', handler)
     runner = web.AppRunner(app)
     await runner.setup()
     self.site = web.TCPSite(runner, host="0.0.0.0", port=8153)
     await self.bot.wait_until_ready()
     await self.site.start()
     logging.info(f"Web server started at PORT: {self.site._port} HOST: {self.site._host}")

    @commands.Cog.listener()
    async def on_ready(self):
     try:
      await self.bot.loop.create_task(self.start())
     except Exception as e:
        logging.error(e)
        return

async def setup(bot):
    await bot.add_cog(Server(bot))