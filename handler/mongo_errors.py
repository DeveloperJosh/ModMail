class MongoErrors(Exception):
    """
    This file will not be used till i think of a way to use it
    """
    def __init__(self):
        pass

    def already_exists(self):
        return f"User with id already exists"

    def not_found(self):
        return f"User with id not found"

    def not_found_list(self):
        return "No users found"

    def not_found_list_blocked(self):
        return "No users found"

    def not_found_list_servers(self):
        return "No servers found"