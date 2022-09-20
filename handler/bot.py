from discord import User
from utils.bot import ModMail
from utils.db import Database

class Bot():
    """
    This file will not be used till i think of a way to use it
    """
    def __init__(self, bot: ModMail):
        self.bot = bot
        self.db = Database()

    async def user_data(self, id, guild_id=None, channel_id=None):
        data = await self.db.find_user(id)
        if data:
            return data
        # if it is false then create a new user data
        user_data = await self.bot.fetch_user(id)
        if not user_data:
            return False
        await self.db.add_user(id, {'ticket': int(channel_id), 'guild': int(guild_id), 'name': user_data.name, 'discriminator': user_data.discriminator, 'avatar': str(user_data.avatar.url)}) # type: ignore