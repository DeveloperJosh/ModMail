from enum import Flag
from sys import prefix
import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()
class Database:
    """
    This class is used to handle all the database stuff
    """
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
        self.db = self.client["mail"]
        self.collection = self.db["mail"]
        self.blocked = self.db["blocked"]
        self.users = self.db["users"]
        self.servers = self.db["servers"]
        self.commands = self.db["commands"]
        self.opt_out = self.db["optout"]
        self.vote = self.db["vote"]

    async def block(self, id):
        if await self.blocked.find_one({"_id": id}):
            return False
        await self.blocked.insert_one({"_id": id})
        return True

    async def unblock(self, id):
        if await self.blocked.find_one({"_id": id}):
            await self.blocked.delete_one({"_id": id})
            return True
        return False

    async def is_blocked(self, id):
        if await self.blocked.find_one({"_id": id}):
            return True
        return False

    async def is_blocked_list(self, id):
        # list all ids in a list
        list = await self.blocked.find({}).to_list(None)
        if list:
            return list
        return False

    ################################################
    
    async def find_user(self, id):
        # return the user data
        data = await self.users.find_one({"_id": id})
        if data:
            return data
        return False

    async def add_user(self, id, data):
        if await self.users.find_one({"_id": id}):
            return False
        things = {"_id": id}
        things.update(data)
        await self.users.insert_one(things)
        return True
    
    async def update_user(self, id, data):
        if await self.users.find_one({"_id": id}):
            await self.users.update_one({"_id": id}, {"$set": data})
            return True
        return False

    async def delete_user(self, id):
        if await self.users.find_one({"_id": id}):
            await self.users.delete_one({"_id": id})
            return True
        return False

    async def get_users(self):
        #try to show all users in a list
        list = await self.users.find({}).to_list(None)
        return list

    ################################################

    async def find_ticket(self, id):
        # return the ticket data
        data = await self.users.find_one({"ticket": id})
        if data:
            return data
        return False
        
    # testing
    async def save_transcript(self, id, data):
        if await self.find_server(id):
            await self.servers.update_one({"_id": id}, {"$set": {"transcript": data}})
            return True
        return False

    async def optout(self, id):
        if await self.opt_out.find_one({"_id": id}):
            return False
        await self.opt_out.insert_one({"_id": id, "optout": True})
        return True

    async def find_opt(self, id):
        # return the opt data
        data = await self.opt_out.find_one({"_id": id})
        if data:
            return data
        return False

    async def optin(self, id):
        if await self.opt_out.find_one({"_id": id}):
            await self.opt_out.delete_one({"_id": id})
            return True
        return False

    ################################################

    async def find_server(self, id):
        # return the server data
        data = await self.servers.find_one({"_id": id})
        if data:
            return data
        return False

    async def create_server(self, id, data):
        if await self.find_server(id):
        #if await self.servers.find_one({"_id": id}):
            return False
        things = {"_id": id}
        things.update(data)
        await self.servers.insert_one(things)
        return True

    async def update_server(self, id, data):
        if await self.servers.find_one({"_id": id}):
            await self.servers.update_one({"_id": id}, {"$set": data})
            return True
        return False

    async def delete_server(self, id):
        if await self.servers.find_one({"_id": id}):
            await self.servers.delete_one({"_id": id})
            return True
        return False

    ################################################

    async def find_command(self, id, command):
        # return the command data
        data = await self.commands.find_one({"guild": id, "command": command})
        if data:
            return data
        return False

    async def find_commands(self, id):
        # try to show all commands in a list
        list = await self.commands.find({"guild": id}).to_list(None)
        return list

    async def max_commands(self, id):
        # max commands are 5
        list = await self.find_commands(id)
        if list:
            if len(list) >= 5:
                return True
        return False

    async def create_command(self, id, data):
        if await self.find_command(id, data["command"]):
            return False
        things = {"guild": id}
        things.update(data)
        await self.commands.insert_one(things)
        return True

    async def update_command(self, id, command, content):
        if await self.find_command(id, command):
            #await self.commands.update_one({"guild": id, "command": command}, {"$set": data})
            await self.commands.update_one({"guild": id, "command": command}, {"$set": {"text": content}})
            return True
        return False

    async def delete_command(self, id, command):
        if await self.find_command(id, command):
            await self.commands.delete_one({"guild": id, "command": command})
            return True
        return False

    ################################################

    async def find_vote(self, id):
        # return the vote data
        data = await self.vote.find_one({"_id": id})
        if data:
            return data
        return False

    async def create_vote(self, id, data):
        if await self.find_vote(id):
            return False
        things = {"_id": id}
        things.update(data)
        await self.vote.insert_one(things)
        return True

    async def update_vote(self, id, data):
        if await self.vote.find_one({"_id": id}):
            await self.vote.update_one({"_id": id}, {"$set": data})
            return True
        return False

    async def delete_vote(self, id):
        if await self.vote.find_one({"_id": id}):
            await self.vote.delete_one({"_id": id})
            return True
        return False