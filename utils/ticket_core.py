import discord
from discord.ext import commands
from utils.db import Database
from utils.bot import ModMail
from typing import Optional, Dict, Union

"""
I use # type: ignore to ignore the errors that are caused by the fact that my vscode is broken.
"""

class Ticket():
    """Ticket handlier, This will use the functions from utiles.db to handle tickets"""
    def __init__(self, bot: ModMail) -> None:
        self.db = Database()
        self.bot = bot

    async def send_mondmail_message(self, channel: discord.TextChannel, message: Union[discord.Message, str], user_name) -> discord.Message:  # type: ignore
        """Sends the user message to the ticket channel"""
        webhook = await self.webhook(channel.id, user_name)
        if isinstance(message, discord.Message):
            if message.attachments:
                attachments = []
                for attachment in message.attachments:
                    attachments.append(await attachment.to_file())
                return await webhook.send(content=message.content, username=message.author.display_name, avatar_url=message.author.avatar.url, files=attachments)  # type: ignore
            return await webhook.send(content=message.content, username=message.author.display_name, avatar_url=message.author.avatar.url)  # type: ignore

    async def create(self, id, guild_id, message: Optional[discord.Message] = None) -> bool:
        """This function creates a ticket"""
        data = await self.bot.fetch_user(id)
        if data:
            guild_data = await self.db.find_server(int(guild_id))
            guild = self.bot.get_guild(int(guild_id))

            channel = await guild.create_text_channel(name=f"ticket-{message.author.id}", category=guild.get_channel(guild_data['category'])) # type: ignore
            await self.webhook(channel.id, message.author.display_name)
            await channel.set_permissions(guild.default_role, read_messages=False, send_messages=False) # type: ignore
            role = guild.get_role(guild_data['staff_role']) # type: ignore
            await channel.set_permissions(role, read_messages=True, send_messages=True) # type: ignore
            try:
             await self.db.add_user(id, {"ticket": int(channel.id), "guild": int(guild_id), "name": data.name, "discriminator": data.discriminator, "avatar": str(data.avatar.url)}) # type: ignore
            except Exception as e:
                print(e)

            embed = discord.Embed(title="Ticket Open", description=f"You have opened a ticket. Please wait for a staff member to reply.", color=0x00ff00)
            embed.set_footer(text="Modmail")
            await message.author.send(embed=embed) # type: ignore

            channel_id = self.bot.get_channel(int(channel.id))

            embed = discord.Embed(title=f"```User ID: {id}```", color=discord.Color.blurple())
            time = data.created_at.strftime("%b %d, %Y")
            embed.add_field(name="User Name", value=data.name, inline=False)
            embed.add_field(name="Account Age", value=f"{time}", inline=False)
            if message.content != "": # type: ignore
             embed.add_field(name="Message", value=f"{message.content}", inline=True) # type: ignore
            embed.set_footer(text="Modmail")

            await channel_id.send(f"<@&{guild_data['staff_role']}>") # type: ignore
            images = []
            if message.attachments: # type: ignore
                for attachment in message.attachments: # type: ignore
                    images.append(await attachment.to_file())
                await channel_id.send(files=images) # type: ignore
            await channel_id.send(embed=embed) # type: ignore
            return True
        print("User not found")
        return False

    async def check(self, id) -> bool:
        """This function checks if the user has a ticket"""
        data = await self.db.find_user(id)
        if data:
            return True
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
