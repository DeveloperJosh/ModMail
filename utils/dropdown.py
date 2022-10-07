import discord
from discord.ext import commands
from typing import Union, Optional, List

class Confirm(discord.ui.View):
    def __init__(self, context: commands.Context, timeout: Optional[int] = 300, user: Optional[Union[discord.Member, discord.User]] = None):
        super().__init__(timeout=timeout)
        self.value = None
        self.context = context
        self.user = user or self.context.author

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def yes(self, b, i):
        self.value = True
        self.stop()

    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def no(self, b, i):
        self.value = False
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("You cannot interact in other's commands.", ephemeral=True)
            return False
        return True

class ServersDropdown(discord.ui.Select):
    def __init__(self, servers: List[discord.Guild]):
        options = [discord.SelectOption(label=server.name, value=str(server.id), description=f"Server ID: {server.id}") for server in servers]
        super().__init__(placeholder="Please select a guild to start a modmail thread with.", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        self.selected_options = [option for option in self.values]
        await interaction.response.send_message("Please press the continue button to continue.", ephemeral=True)

class ServersDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.yes = False

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.blurple, row=1)
    async def c(self, i: discord.Interaction, b: discord.ui.Button):
        if not self.children[2].values:  # type: ignore
            return await i.response.send_message("Please select a server first.", ephemeral=True)
        self.yes = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, row=1)
    async def c_(self, i: discord.Interaction, b: discord.ui.Button):
        self.stop()

class RolesDropdown(discord.ui.Select):
    def __init__(self, roles: List[discord.Role]):
        options = [discord.SelectOption(label=role.name, value=str(role.id), description=f"Role ID: {role.id}") for role in roles]
        super().__init__(placeholder="Please select a role to start a modmail thread with.", options=options, row=0)
        # show the name of what was selected
        self.selected_options = []

    async def callback(self, interaction: discord.Interaction):
        self.selected_options = [option for option in self.values]
        await interaction.response.send_message("Please press the continue button to continue.", ephemeral=True)

class RolesDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.yes = False

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.blurple, row=1)
    async def c(self, i: discord.Interaction, b: discord.ui.Button):
        if not self.children[2].values:  # type: ignore
            return await i.response.send_message("Please select a server first.", ephemeral=True)
        self.yes = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, row=1)
    async def c_(self, b, i):
        self.stop()

class ChannelsDropdown(discord.ui.Select):
    def __init__(self, channels: List[discord.TextChannel]):
        options = [discord.SelectOption(label=channel.name, value=str(channel.id), description=f"Channel ID: {channel.id}") for channel in channels]
        super().__init__(placeholder="Please select a channel to start a modmail thread with.", options=options, row=0)
        # show the name of what was selected
        self.selected_options = []

    async def callback(self, interaction: discord.Interaction):
        self.selected_options = [option for option in self.values]
        await interaction.response.send_message("Please press the continue button to continue.", ephemeral=True)

class ChannelsDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.yes = False

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.blurple, row=1)
    async def c(self, i: discord.Interaction, b: discord.ui.Button):
        if not self.children[2].values:  # type: ignore
            return await i.response.send_message("Please select a channel first.", ephemeral=True)
        self.yes = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, row=1)
    async def c_(self, b, i):
        self.stop()

class CategoryDropdown(discord.ui.Select):
    def __init__(self, categories: List[discord.CategoryChannel]):
        options = [discord.SelectOption(label=category.name, value=str(category.id), description=f"Category ID: {category.id}") for category in categories]
        super().__init__(placeholder="Please select a category to start a modmail thread with.", options=options, row=0)
        # show the name of what was selected
        self.selected_options = []

    async def callback(self, interaction: discord.Interaction):
        self.selected_options = [option for option in self.values]
        await interaction.response.send_message("Please press the continue button to continue.", ephemeral=True)

class CategoryDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.yes = False

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.blurple, row=1)
    async def c(self, i: discord.Interaction, b: discord.ui.Button):
        if not self.children[2].values:  # type: ignore
            return await i.response.send_message("Please select a category first.", ephemeral=True)
        self.yes = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, row=1)
    async def c_(self, b, i):
        self.stop()
