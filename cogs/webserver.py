import logging
from aiohttp import ClientSession, web
import asyncio
import discord 
from discord.ext import commands
from utils.db import Database
import hikari
import aiohttp_cors
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
load_dotenv()
        
class Server(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = Database()
        self.rest_api = hikari.RESTApp()
        self.site = None
        self.BASE = "https://discord.com/api"
        self.REDIRECT_URI = "http://localhost:8153/callback"
        self.cors_thing = {
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        }
    async def stats(self, request):
        return web.json_response({"guild_count": len(self.bot.guilds), "ping": round(self.bot.latency * 1000)})

    async def login(self, request):
        # login to discord and get the token
        # use ClientSession to get the token
        return web.HTTPFound(location=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&redirect_uri={self.REDIRECT_URI}&response_type=code&scope=identify%20guilds%20guilds.join")

    async def get_access_token(self, request, code: str):
        # save the token to the headers
        async with ClientSession() as session:
            async with session.post(f"{self.BASE}/oauth2/token", data={
                "client_id": self.bot.user.id,
                "client_secret": os.getenv("CLIENT_SECRET"),
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.REDIRECT_URI,
                "scope": "identify guilds guilds.join"
            }) as resp:
                data = await resp.json()
                return data

    async def callback(self, request):
        # if token is valid, then get the user
        # if token is invalid, then redirect to login
        code = request.query.get("code")
        if code is None:
            raise web.HTTPBadRequest()
        data = await self.get_access_token(request, code)
        if data.get("error") is not None:
            return web.HTTPFound(location="/login")
        access_token = data.get("access_token")
        if access_token is None:
            raise web.HTTPBadRequest()
        # add the token to the headers
        headers = {
            "access_token": access_token
        }
        # send to /user
        return web.HTTPFound(location="/user", headers=headers)

    async def update_category(self, request):
      ## url/guild_id/category_id
      guild_id = request.match_info.get("guild_id")
      category_id = request.match_info.get("category_id")
      guild = self.bot.get_guild(int(guild_id))
      if guild is None:
        return web.json_response({"error": "Guild not found"})
      category = guild.get_channel(int(category_id))
      if category is None:
        return web.json_response({"error": "Category not found"})
      await self.db.update_server(guild.id, {"category": category.id})
      return web.json_response({"success": "Category updated"})

    async def home(self, request):
        return web.Response(text="Hello World")

    async def start(self):
     app = web.Application()
     app.router.add_get('/', self.home)
     app.router.add_get('/stats', self.stats)
     app.router.add_post('/update_category/{guild_id}/{category_id}', self.update_category)
     app.router.add_get('/login', self.login)
     app.router.add_get('/callback', self.callback)
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