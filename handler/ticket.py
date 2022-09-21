import discord
from discord.ext import commands
from utils.db import Database
from utils.bot import ModMail

class Ticket():
    """Ticket handlier, This will use the functions from utiles.db to handle tickets"""
    def __init__(self, bot: ModMail) -> None:
        self.db = Database()
        self.bot = bot

    async def create(self, id, channel_id, guild_id):
        """This function creates a ticket"""
        data = await self.bot.fetch_user(id)
        if data:
            await self.db.add_user(id, {"ticket": int(channel_id), "guild": int(guild_id), "name": data.name, "discriminator": data.discriminator, "avatar": str(data.avatar.url)}) # type: ignore
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
            return webhooks[0]
      return await channel.create_webhook(name=webhook_name)  # type: ignore
