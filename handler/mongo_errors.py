"""
This file will not be used till i think of a way to use it
"""
class MongoErrors(Exception):
    def __init__(self):
        pass

    async def already_exists(self, id):
        return f"User with id {id} already exists"