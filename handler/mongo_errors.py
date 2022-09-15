class MongoErrors(Exception):
    def __init__(self, message):
        self.message = message

    async def not_found(self):
        return self.message

    async def already_exists(self):
        return self.message