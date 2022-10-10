from uuid import uuid4
from io import BytesIO
import discord
from discord.ext import commands
from utils.db import Database
from utils.bot import ModMail
from typing import Optional, Dict, Union
from .exceptions import UserAlreadyInAModmailThread

"""
I use # type: ignore to ignore the errors that are caused by the fact that my vscode is broken.
"""

class Ticket():
    """Ticket handlier, This will use the functions from utiles.db to handle tickets"""
    def __init__(self, bot: ModMail) -> None:
        self.db = Database()
        self.bot = bot

    async def send_mondmail_message(self, channel: discord.TextChannel, message: Union[discord.Message, str], webhook_name) -> discord.Message:  # type: ignore
        """Sends the user message to the ticket channel"""
        webhook = await self.webhook(channel.id, webhook_name)
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
        # check if the user has a ticket
        if await self.check(id) is True:
            raise UserAlreadyInAModmailThread(data)
        if data:
            guild_data = await self.db.find_server(int(guild_id))
            guild = self.bot.get_guild(int(guild_id))
            try:
             channel = await guild.create_text_channel(name=f"ticket-{message.author.id}", category=guild.get_channel(guild_data['category'])) # type: ignore
             await channel.set_permissions(guild.default_role, read_messages=False, send_messages=False) # type: ignore
             role = guild.get_role(guild_data['staff_role']) # type: ignore
             await channel.set_permissions(role, read_messages=True, send_messages=True) # type: ignore
            # give bot perms in the channel
             await channel.set_permissions(self.bot.user, read_messages=True, send_messages=True) # type: ignore
            except Exception as e:
                print(e)
            try:
             await self.db.add_user(id, {"ticket": int(channel.id), "guild": int(guild_id), "name": data.name, "discriminator": data.discriminator, "avatar": str(data.avatar.url)}) # type: ignore
            except Exception as e:
                print(e)

            embed = discord.Embed(title="Ticket Open", description=f"You have opened a ticket. Please wait for a staff member to reply.", color=0x00ff00)
            embed.set_footer(text="Modmail")
            await message.author.send(embed=embed) # type: ignore

            channel_id = self.bot.get_channel(int(channel.id))
            await self.webhook(channel.id, "Modmail") # type: ignore

            embed = discord.Embed(title=f"```User ID: {id}```", color=discord.Color.blurple())
            time = data.created_at.strftime("%b %d, %Y")
            embed.add_field(name="User Name", value=data.name, inline=False)
            embed.add_field(name="Account Age", value=f"{time}", inline=False)
            if message.content != "": # type: ignore
             embed.add_field(name="Message", value=f"{message.content}", inline=True) # type: ignore
            embed.set_footer(text="Modmail")
            try:
             await channel_id.send(f"<@&{guild_data['staff_role']}>\nUsing `{self.bot.command_prefix}` in this ticket will block messages from being sent") # type: ignore
            except Exception as e:
                print(e)
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
        data = await self.db.find_user(id) or await self.db.find_ticket(id)
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

    async def create_transcript(self, channel: discord.TextChannel, guild, userId: int) -> None:
     """This function creates a transcript of the ticket"""

     # TODO: Add the optout feature to the transcript

     # if user is in self.db.find_opt() remove them from the transcript
     if await self.db.find_opt(userId):
      data = await self.db.find_server(channel.guild.id)
      transcript_db_channel = self.bot.get_channel(data['transcript_channel'])  # type: ignore
      if transcript_db_channel is None:
        return
      await transcript_db_channel.send("Sorry, But the Owner of this ticket has opted out of the transcript system, So no transcript was made.")  # type: ignore
      await channel.delete()
      return

     # Making the file
     channel = self.bot.get_channel(channel.id)  # type: ignore
     text = ""
     all_msgs = [all_msg async for all_msg in channel.history(limit=None)]
     for msg in all_msgs[::-1]:
        content = msg.content.replace("\n\n", "\n\n")
        text += f"{msg.author} | {channel.name[7:] if len(str(msg.author).split('#')) == 3 else msg.author.id} | {content}\n\n"
     data = await self.db.find_server(channel.guild.id)
     transcript_db_channel = self.bot.get_channel(data['transcript_channel'])  # type: ignore
     if transcript_db_channel is None:
        return
     randomly_generator_id = str(uuid4())
     msg = await transcript_db_channel.send(content=f"To see more info about the ticket do `{self.bot.command_prefix}transcripts {randomly_generator_id}`", file=discord.File(BytesIO(text.encode("utf-8")), filename=f"{channel.name}.txt"))  # type: ignore
     transcript = await self.db.find_server(guild.id)
     if not transcript['transcripts']:  # type: ignore
      transcript['transcripts'] = {}  # type: ignore
     transcript['transcripts'][randomly_generator_id] = msg.jump_url  # type: ignore
     await self.db.update_server(guild.id, transcript)  # type: ignore
     await channel.delete()