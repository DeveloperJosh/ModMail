import logging
import asyncio
from unicodedata import category
import discord
from utils.db import Database
import hikari
import aiohttp_cors
import ast
from typing import List
from discord.ext import commands
from utils.bot import ModMail
from aiohttp import web, ClientSession
import os
from dotenv import load_dotenv
load_dotenv()

class Guild:
    def __init__(self, id: str, name: str, icon: str, owner: bool, permissions: int, features: List[str], permissions_new: str):
        self.id: str = id
        self.name: str = name
        self.icon: str = icon
        self.owner: bool = owner
        self.permissions: int = permissions
        self.features: List[str] = features
        self.permissions_new: str = permissions_new
        self.invited: bool = False

    def __str__(self) -> str:
        return f"<Guild name='{self.name}' id={self.id}>"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def icon_url(self) -> str:
        return f"https://cdn.discordapp.com/icons/{self.id}/{self.icon}.png" if self.icon is not None else None  # type: ignore


class WebServer(commands.Cog):
    def __init__(self, bot: ModMail):
        self.client = bot
        self.rest_api = hikari.RESTApp()
        self.api = None
        self.db = Database()
        self.BASE = "https://discord.com/api"
        #self.REDIRECT_URI = "https://mail-hook.xyz/callback"
        self.REDIRECT_URI = "http://localhost:3000/callback"
        self.cors_thing = {
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        }

    def filter_guilds(self, user_guilds: List[Guild], bot_guilds: List[discord.Guild]) -> List[Guild]:
        mutual_guilds: List[Guild] = []
        bot_guild_ids = [g.id for g in bot_guilds]
        for guild in user_guilds:
            if int(guild.id) in bot_guild_ids:
                guild.invited = True
            else:
                guild.invited = False
            mutual_guilds.append(guild)
        return [g for g in mutual_guilds if g.permissions & hikari.Permissions.MANAGE_GUILD]

    async def get_access_token(self, code: str) -> dict:
        async with ClientSession() as session:
            async with session.post(
                f"{self.BASE}/oauth2/token",
                data={
                    "client_id": str(self.client.user.id),
                    "client_secret": os.getenv("CLIENT_SECRET"),
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.REDIRECT_URI,
                },
            ) as resp:
                return await resp.json()

    async def get_user(self, token: str) -> hikari.OwnUser:
        async with self.rest_api.acquire(token) as client:
            return await client.fetch_my_user()

    async def get_user_guilds(self, token: str) -> List[Guild]:
        async with ClientSession() as session:
            async with session.get(
                f"{self.BASE}/users/@me/guilds",
                headers={"Authorization": f"Bearer {token}"},
            ) as resp:
                data = await resp.json()
                return [Guild(**g) for g in data]

    async def callback(self, request: web.Request):
        code = (await request.json()).get("code").get("code")
        if code is None:
            raise web.HTTPBadRequest()
        data = await self.get_access_token(code)
        print(data)
        return web.json_response({"access_token": data.get("access_token")})

    async def get_own_user(self, request: web.Request):
        access_token = request.headers.get("access_token")
        if access_token is None:
            raise web.HTTPBadRequest()
        user = await self.get_user(access_token)
        return web.json_response({
            "id": str(user.id),
            "username": user.username,
            "discriminator": user.discriminator,
            "avatar": str(user.avatar_url)
        })

    async def get_guilds(self, request: web.Request):
        access_token = request.headers.get("access_token")
        if access_token is None:
            raise web.HTTPBadRequest()

        user_guilds = await self.get_user_guilds(access_token)
        bot_guilds = self.client.guilds
        final_guilds = self.filter_guilds(user_guilds, bot_guilds)

        return web.json_response({
            "guilds": [{
                "id": g.id,
                "name": g.name,
                "icon_url": g.icon_url,
                "invited": g.invited
            } for g in final_guilds]
        })

    async def update_mod_role(self, request: web.Request):
        susu = await request.json()
        role_id = susu.get("role_id")
        guild_id = susu.get("guild_id")
        access_token = susu.get("access_token")
        user = await self.get_user(access_token)
        user_id = user.id
        if role_id is None or guild_id is None:
            raise web.HTTPBadRequest()
        guild = self.client.get_guild(int(guild_id))
        if guild is None:
            return web.json_response({"error": "Guild not found"})
        member = guild.get_member(int(user_id))
        if member is None:
            return web.json_response({"error": "Not authorized"})
        if not member.guild_permissions.manage_guild:
            return web.json_response({"error": "Not authorized"})
        role = guild.get_role(int(role_id))
        if role is None:
            return web.json_response({"error": "Role not found"})
        #await self.client.mongo.set_guild_data(guild_id=int(guild_id), staff_role=role.id)
        await self.db.update_server(guild.id, {"staff_role": role.id})
        self.client.dispatch("mod_role_update", guild, role)
        return web.json_response({"success": True})

    async def update_category(self, request: web.Request):
        susu = await request.json()
        category_id = susu.get("category_id")
        guild_id = susu.get("guild_id")
        access_token = susu.get("access_token")
        user = await self.get_user(access_token)
        user_id = user.id
        if category_id is None or guild_id is None:
            raise web.HTTPBadRequest()
        guild = self.client.get_guild(int(guild_id))
        if guild is None:
            return web.json_response({"error": "Guild not found"})
        member = guild.get_member(int(user_id))
        if member is None:
            return web.json_response({"error": "Not authorized"})
        if not member.guild_permissions.manage_guild:
            return web.json_response({"error": "Not authorized"})
        category = guild.get_channel(int(category_id))
        if category is None:
            return web.json_response({"error": "Category not found"})
        #await self.client.mongo.set_guild_data(guild_id=int(guild_id), category=category.id)
        await self.db.update_server(guild.id, {"category": category.id})
        self.client.dispatch("category_update", guild, category)
        return web.json_response({"success": True})

    async def update_transcript_channel(self, request: web.Request):
        susu = await request.json()
        channel_id = susu.get("channel_id")
        guild_id = susu.get("guild_id")
        access_token = susu.get("access_token")
        user = await self.get_user(access_token)
        user_id = user.id
        if channel_id is None or guild_id is None:
            raise web.HTTPBadRequest()
        guild = self.client.get_guild(int(guild_id))
        if guild is None:
            return web.json_response({"error": "Guild not found"})
        member = guild.get_member(int(user_id))
        if member is None:
            return web.json_response({"error": "Not authorized"})
        if not member.guild_permissions.manage_guild:
            return web.json_response({"error": "Not authorized"})
        channel = guild.get_channel(int(channel_id))
        if channel is None:
            return web.json_response({"error": "Channel not found"})
        #await self.client.mongo.set_guild_data(guild_id=int(guild_id), transcripts=channel.id)
        await self.db.update_server(guild.id, {"transcript_channel": channel.id})
        self.client.dispatch("transcript_channel_update", guild, channel)
        return web.json_response({"success": True})

    async def check_setup(self, request: web.Request):
        guild_id = request.headers.get("guild_id")
        access_token = request.headers.get("access_token")
        if guild_id is None or access_token is None:
            raise web.HTTPBadRequest()
        user = await self.get_user(access_token)
        user_id = user.id
        try:
            guild_id = int(guild_id)
            user_id = int(user_id)
        except ValueError:
            return web.json_response({"error": "Invalid guild id"})
        guild = self.client.get_guild(guild_id)
        if guild is None:
            return web.json_response({"error": "Guild not found"})
        member = guild.get_member(user_id)
        if member is None:
            return web.json_response({"error": "You are not in the guild."})
        if not member.guild_permissions.manage_guild:
            return web.json_response({"error": "You need manage_guild permissions to do that."})
        guild_data = await self.db.get_server(guild_id, raise_error=False)
        if guild_data is None:
            return web.json_response({"setup": False})
        is_setup = await self.db.get_server(guild_id, raise_error=False)
        if is_setup is None:
            return web.json_response({"setup": False})
        elif not None:
            return web.json_response({"setup": True})

    async def setup(self, request: web.Request):
        guild_id = request.headers.get("guild_id")
        access_token = request.headers.get("access_token")
        if guild_id is None or access_token is None:
            raise web.HTTPBadRequest()
        user = await self.get_user(access_token)
        user_id = user.id
        try:
            guild_id = int(guild_id)
            user_id = int(user_id)
        except ValueError:
            return web.json_response({"error": "Invalid guild id"})
        guild = self.client.get_guild(guild_id)
        if guild is None:
            return web.json_response({"error": "Guild not found"})
        member = guild.get_member(user_id)
        if member is None:
            return web.json_response({"error": "You are not in the guild."})
        if not member.guild_permissions.manage_guild:
            return web.json_response({"error": "You need manage_guild permissions to do that."})
        guild_data = await self.db.get_server(guild_id, raise_error=False)
        if guild_data is None:
            return web.json_response({"setup": False})
        is_setup = await self.db.get_server(guild_id, raise_error=False)
        if is_setup is None:
            return web.json_response({"setup": False})
        elif not None:
            return web.json_response({"setup": True})

    async def setup_guild(self, request: web.Request):
        print("setup_guild")
        guild_id = request.headers.get("guild_id")
        staff_role_id = request.headers.get("staff_role_id")
        category_id = request.headers.get("category_id")
        transcripts_id = request.headers.get("transcripts_id")
        access_token = request.headers.get("access_token")
        if guild_id is None or staff_role_id is None or category_id is None or transcripts_id is None or access_token is None:
            raise web.HTTPBadRequest()
        user = await self.get_user(access_token)
        user_id = user.id
        try:
            guild_id = int(guild_id)
            staff_role_id = int(staff_role_id)
            category_id = int(category_id)
            transcripts_id = int(transcripts_id)
        except ValueError:
            return web.json_response({"error": "Invalid guild id or role id or category id or transcripts id"})
        guild = self.client.get_guild(guild_id)
        if guild is None:
            return web.json_response({"error": "Guild not found"})
        member = guild.get_member(user_id)
        if member is None:
            return web.json_response({"error": "Unauthorized"})
        if not member.guild_permissions.manage_guild:
            return web.json_response({"error": "Unauthorized"})
        staff_role = guild.get_role(staff_role_id)
        if staff_role is None:
            return web.json_response({"error": "Staff role not found"})
        category = guild.get_channel(category_id)
        if category is None:
            return web.json_response({"error": "Category not found"})
        transcripts = guild.get_channel(transcripts_id)
        if transcripts is None:
            return web.json_response({"error": "Transcripts channel not found"})
        if not category.permissions_for(guild.me).manage_channels:
            return web.json_response({"error": "I don't have permissions to create channels in the category."})
        if not category.permissions_for(guild.me).manage_webhooks:
            return web.json_response({"error": "I don't have permissions to create webhooks in the category."})
        if not category.permissions_for(guild.me).read_message_history:
            return web.json_response({"error": "I don't have permissions to read message history in the category."})
        if not category.permissions_for(guild.me).use_external_emojis:
            return web.json_response({"error": "I don't have permissions to use external emojis in the category."})
        if not category.permissions_for(guild.me).add_reactions:
            return web.json_response({"error": "I don't have permissions to add reactions in the category."})
        if not category.permissions_for(guild.me).read_messages:
            return web.json_response({"error": "I don't have permissions to read messages in the category."})
        if not category.permissions_for(guild.me).send_messages:
            return web.json_response({"error": "I don't have permissions to send messages in the category."})
        if not transcripts.permissions_for(guild.me).read_messages or not transcripts.permissions_for(guild.me).send_messages:
            return web.json_response({"error": "I don't have permissions to read messages or send messages in the transcripts channel."})
        data = {
            "staff_role": staff_role.id,
            "category": category.id,
            "transcript_channel": transcripts.id
        }
        #await self.client.mongo.set_guild_data(guild_id=guild_id, **data)
        await self.db.create_server(guild.id, data)
        return web.json_response({"success": True, "message": "Guild setup complete." if guild.me.guild_permissions.administrator else "The guild setup is complete, it is recommended that you grant me administrator permissions for the best experience."})

    async def get_guild_data(self, request: web.Request):
        guild_id = request.headers.get("guild_id")
        access_token = request.headers.get("access_token")
        if guild_id is None or access_token is None:
            raise web.HTTPBadRequest()
        try:
            user = await self.get_user(access_token)
        except hikari.UnauthorizedError:
            return web.json_response({"error": "Unauthorized"})
        user_id = user.id
        print(user_id, guild_id)
        try:
            int(guild_id)
            int(user_id)
        except ValueError:
            return web.json_response({"error": "Invalid guild id or user id"})
        guild = self.client.get_guild(int(guild_id))
        if guild is None:
            return web.json_response({"error": "Guild not found"})
        member = guild.get_member(int(user_id))
        if member is None:
            return web.json_response({"error": "Member not found"})
        if not member.guild_permissions.manage_guild:
            return web.json_response({"error": "Insufficient permissions"})
        guild_data = await self.db.find_server(guild.id)
        if guild_data is not False:
            modrole = guild.get_role(guild_data['staff_role'])
            ticket_category = guild.get_channel(guild_data['category'])
            transcript_channel = guild.get_channel(guild_data['transcript_channel'])
        else:
            # send to url/set/id
            return web.HTTPFound(location=f"/setup/{guild.id}")
        return web.json_response({
            "id": str(guild.id),
            "name": guild.name,
            "description": guild.description,
            "icon": guild.icon.url if guild.icon is not None else "https://cdn.discordapp.com/embed/avatars/0.png",
            "banner": guild.banner.url if guild.banner is not None else None,
            "members": guild.member_count,
            "roles": len(guild.roles),
            "channels": len(guild.channels),
            "roleList": [{
                "id": str(r.id),
                "name": r.name,
                "color": str(r.color),
            } for r in guild.roles if r != guild.default_role][::-1],
            "categoryList": [{
                "id": str(c.id),
                "name": c.name
            } for c in guild.categories],
            "channelList": [{
                "id": str(c.id),
                "name": c.name
            } for c in guild.text_channels],
            "owner": {
                "id": str(guild.owner.id),
                "username": guild.owner.name,
                "discriminator": guild.owner.discriminator,
                "avatar": guild.owner.display_avatar.url
            } if guild.owner is not None else None,
            "settings": {
                "modRole": {
                    "id": str(modrole.id),
                    "name": modrole.name,
                    "color": str(modrole.color),
                } if modrole is not None else None,
                "ticketCategory": {
                    "id": str(ticket_category.id),
                    "name": ticket_category.name,
                } if ticket_category is not None else None,
                "transcriptChannel": {
                    "id": str(transcript_channel.id),
                    "name": transcript_channel.name,
                },
            },
        })

    async def toggle_modping(self, request: web.Request):
        susu = await request.json()
        guild_id = susu.get("guild_id")
        access_token = susu.get("access_token")
        if guild_id is None or access_token is None:
            raise web.HTTPBadRequest()
        user = await self.get_user(access_token)
        user_id = user.id
        guild = self.client.get_guild(int(guild_id))
        if guild is None:
            return web.json_response({"error": "Guild not found"})
        member = guild.get_member(int(user_id))
        if member is None:
            return web.json_response({"error": "Not authorized"})
        if not member.guild_permissions.manage_guild:
            return web.json_response({"error": "Not authorized"})
        guild_data = await self.db.find_server(guild.id)
        await self.db.update_server(guild.id, {"modping": not guild_data['modping']})

    async def bot_stats(self, request: web.Request):
        return web.json_response({
            "guilds": len(self.client.guilds),
            "users": len(self.client.users),
            "ping": round(self.client.latency * 1000, 2),
        })
    async def start_server(self):
        app = web.Application()
        cors = aiohttp_cors.setup(app)

        callback_resource = cors.add(app.router.add_resource("/oauth/callback"))
        get_own_user_resource = cors.add(app.router.add_resource("/users/me"))
        get_guilds_resource = cors.add(app.router.add_resource("/guilds"))
        get_guild_data_resource = cors.add(app.router.add_resource("/guild"))
        check_setup_resource = cors.add(app.router.add_resource("/check_setup"))
        setup_guild_resource = cors.add(app.router.add_resource("/setup_guild"))
        bot_stats_resource = cors.add(app.router.add_resource("/stats"))
        update_mod_role_resource = cors.add(app.router.add_resource("/update_mod_role"))
        update_ping_staff_resource = cors.add(app.router.add_resource("/update_ping_staff"))
        update_category_resource = cors.add(app.router.add_resource("/update_category"))
        update_transcripts_resource = cors.add(app.router.add_resource("/update_transcripts"))

        cors.add(callback_resource.add_route("POST", self.callback), self.cors_thing)
        cors.add(get_own_user_resource.add_route("GET", self.get_own_user), self.cors_thing)
        cors.add(get_guilds_resource.add_route("GET", self.get_guilds), self.cors_thing)
        cors.add(get_guild_data_resource.add_route("GET", self.get_guild_data), self.cors_thing)
        cors.add(check_setup_resource.add_route("GET", self.check_setup), self.cors_thing)
        cors.add(setup_guild_resource.add_route("POST", self.setup_guild), self.cors_thing)
        cors.add(setup_guild_resource.add_route("GET", self.setup_guild), self.cors_thing)
        cors.add(bot_stats_resource.add_route("GET", self.bot_stats), self.cors_thing)
        cors.add(update_mod_role_resource.add_route("POST", self.update_mod_role), self.cors_thing)
        cors.add(update_ping_staff_resource.add_route("POST", self.toggle_modping), self.cors_thing)
        cors.add(update_category_resource.add_route("POST", self.update_category), self.cors_thing)
        cors.add(update_transcripts_resource.add_route("POST", self.update_transcript_channel), self.cors_thing)

        runner = web.AppRunner(app)
        await runner.setup()

        self.api = web.TCPSite(runner, host="0.0.0.0", port=8153)
        await self.client.wait_until_ready()
        await self.api.start()
        logging.info(f"Web server started at PORT: {self.api._port} HOST: {self.api._host}")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.loop.create_task(self.start_server())

async def setup(bot: ModMail):
    cog = WebServer(bot)
    await bot.add_cog(cog)