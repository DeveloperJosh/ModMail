"""
This file will not be used till i think of a way to use it
"""
class MongoErrors(Exception):
    def __init__(self):
        pass

    async def already_exists(self, id):
        return f"User with id {id} already exists"

    async def not_found(self, id):
        return f"User with id {id} not found"

    async def not_found_list(self):
        return "No users found"

    async def not_found_list_blocked(self):
        return "No users found"

    async def not_found_list_servers(self):
        return "No servers found"