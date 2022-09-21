import discord
from discord.ext import commands
from utils.db import Database
from utils.bot import ModMail
from typing import Optional, Dict, Union

class Ticket():
    """Ticket handlier, This will use the functions from utiles.db to handle tickets"""
    def __init__(self, bot: ModMail) -> None:
        self.db = Database()
        self.bot = bot

    async def send_mondmail_message(self, channel: discord.TextChannel, message: Union[discord.Message, str], user_name) -> discord.Message:  # type: ignore
        webhook = await self.webhook(channel.id, user_name)
        if isinstance(message, discord.Message):
            if message.attachments:
                attachments = []
                for attachment in message.attachments:
                    attachments.append(await attachment.to_file())
                return await webhook.send(content=message.content, username=message.author.display_name, avatar_url=message.author.avatar.url, files=attachments)  # type: ignore
            return await webhook.send(content=message.content, username=message.author.display_name, avatar_url=message.author.avatar.url)  # type: ignore

    async def create(self, id, channel_id, guild_id, message: Optional[discord.Message] = None):
        """This function creates a ticket"""
        data = await self.bot.fetch_user(id)
        if data:
            await self.db.add_user(id, {"ticket": int(channel_id), "guild": int(guild_id), "name": data.name, "discriminator": data.discriminator, "avatar": str(data.avatar.url)}) # type: ignore
            guild = await self.db.find_server(int(guild_id))
            channel = self.bot.get_channel(int(channel_id))
            embed = discord.Embed(title=f"```User ID: {id}```", color=discord.Color.blurple())
            time = data.created_at.strftime("%b %d, %Y")
            embed.add_field(name="User Name", value=data.name, inline=False)
            embed.add_field(name="Account Age", value=f"{time}", inline=False)
            if message.content != "": # type: ignore
             embed.add_field(name="Message", value=f"{message.content}", inline=True) # type: ignore
            embed.set_footer(text="Modmail")
            await channel.send(f"<@&{guild['staff_role']}>")  # type: ignore
            images = []
            if message.attachments: # type: ignore
                for attachment in message.attachments:  # type: ignore
                    images.append(await attachment.to_file())
                await channel.send(files=images) # type: ignore
            await channel.send(embed=embed) # type: ignore
            return True
        print("User not found")
        return False

    async def webhook(self, channel_id, webhook_name) -> discord.Webhook:  # type: ignore
      """This function looks for webhooks with the channel id provided and returns the webhook if it finds one, If it doesn't find one it will create one and return it"""
      channel = self.bot.get_channel(channel_id)
      if channel is None:
          raise commands.ChannelNotFound(channel_id)
      webhooks = await channel.webhooks()  # type: ignore
      if webhooks:
            return discord.utils.get(webhooks, name=webhook_name)  # type: ignore
      return await channel.create_webhook(name=webhook_name)  # type: ignore
