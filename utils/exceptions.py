######################################################
# Note: This file made by Nirlep, file from MailHook #
######################################################

import discord # type: ignore
from typing import Optional, Union
from discord.ext.commands import CommandError # type: ignore

class NotSetup(CommandError):
    pass


class ModRoleNotFound(CommandError):
    pass


class TicketCategoryNotFound(CommandError):
    pass

class TicketChannelNotFound(CommandError):
    pass

class TranscriptChannelNotFound(CommandError):
    pass

class UserAlreadyInAModmailThread(CommandError):
    def __init__(self, user: Optional[Union[discord.Member, discord.User]]):
        self.user = user


class DMsDisabled(CommandError):
    def __init__(self, user: discord.Member):
        self.user = user


class NotStaff(CommandError):
    pass


class NotAdmin(CommandError):
    pass


class NoBots(CommandError):
    pass


class GuildOnlyPls(CommandError):
    pass