import discord
from utils.database import db
from discord.ext import commands
from utils.config import guild, staff, logs

class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = guild
        self.staff = staff
        self.logs = logs

    @commands.Cog.listener()
    async def on_message(self, message):
        # mod mail
        if message.author.bot:
            return
        if message.channel.type == discord.ChannelType.private:
            if not db.users.find_one({'_id': message.author.id}):
                    guild = self.bot.get_guild(self.guild)
                    if not db.servers.find_one({'_id': guild.id}):
                        embed = discord.Embed(
                            title="Oh no!",
                            description=f"Oh no! The server {guild.name} is not in the database. Please contact a server admin.",
                            color=discord.Color.red()
                        )
                        await message.author.send(embed=embed)
                        return
                    channel = await guild.create_text_channel(name=f"ticket-{message.author.id}", category=guild.get_channel(db.servers.find_one({'_id': guild.id})['category'])) # type: ignore
                    await channel.set_permissions(guild.default_role, read_messages=False, send_messages=False)
                    await channel.set_permissions(guild.get_role(self.staff), read_messages=True, send_messages=True)
                    db.users.insert_one({'_id': message.author.id, 'ticket': channel.id})
                    embed = discord.Embed(title="Ticket Open", description=f"You have opened a ticket. Please wait for a staff member to reply.", color=0x00ff00)
                    embed.set_footer(text="Modmail")
                    await message.author.send(embed=embed)
                    embed = discord.Embed(title=f"```User ID: {message.author.id}```", color=discord.Color.blurple())
                    time = message.author.created_at.strftime("%b %d, %Y")
                    embed.add_field(name="Account Age", value=f"{time}", inline=False)
                    embed.add_field(name="Message", value=f"{message.content}", inline=True)
                    embed.set_footer(text="Modmail")
                    await channel.send(embed=embed)
                    await channel.create_webhook(name=message.author.name)
                    # webhook = await channel.webhooks()
                    # webhook = webhook[0]
                    # await webhook.send(message.content, username=message.author.name, avatar_url=message.author.avatar.url)

            else:
                # send user message to their ticket
                guild = self.bot.get_guild(self.guild)
                channel = guild.get_channel(db.users.find_one({'_id': message.author.id})['ticket']) # type: ignore
                webhook_in_channel = await channel.webhooks()
                webhook = webhook_in_channel[0]
                await webhook.send(message.content, username=message.author.name, avatar_url=message.author.avatar.url)
                print(f"{message.author.name} sent a message to {channel.name}")


    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def reply(self, ctx, *, message):
        # delete message
        await ctx.message.delete()
        ticket_id = ctx.channel.id
        user_id = db.users.find_one({'ticket': ticket_id})['_id'] # type: ignore
        # dm the user with the message
        user = self.bot.get_user(user_id)
        embed = discord.Embed(title="Ticket Reply", description=f"Staff: {ctx.author.name}\nMessage: {message}", color=0x00ff00)
        embed.set_footer(text="Modmail")
        await user.send(embed=embed)
        webhook = await ctx.channel.webhooks()
        await webhook[0].send(message, username=ctx.author.name, avatar_url=ctx.author.avatar.url)
        print(f"{ctx.author.name} sent a message to {ctx.channel.name}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def areply(self, ctx, *, message):
        await ctx.message.delete()
        ticket_id = ctx.channel.id
        user_id = db.users.find_one({'ticket': ticket_id})['_id'] # type: ignore
        # dm the user with the message 
        user = self.bot.get_user(user_id)
        embed = discord.Embed(title="Ticket Reply", description=f"Message: {message}", color=0x00ff00)
        embed.set_footer(text="Modmail")
        await user.send(embed=embed)
        webhook = await ctx.channel.webhooks()
        await webhook[0].send(message, username=ctx.author.name, avatar_url=ctx.author.avatar.url)
        print(f"{ctx.author.name} sent a message to {ctx.channel.name}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def close(self, ctx):
        id = ctx.message.channel.name.split("-")[1]
        db.users.delete_one({'ticket': ctx.message.channel.id})
        embed = discord.Embed(title="Ticket Closed", description=f"Your ticket has been closed", color=0x00ff00)
        embed.set_footer(text="Modmail")
        user = self.bot.get_user(int(id))
        await user.send(embed=embed)
        await ctx.message.channel.delete()

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Modmail", description="Modmail is a bot that allows you to send messages to staff members in DMs.", color=0x00ff00)
        embed.add_field(name="Commands", value="```\nping - pong\nreply - reply to a ticket\nareply - reply anonymously to a ticket\nclose - close a ticket\nhelp - this help message\nsetup - sets up the server\nreset - removes all data from teh db```", inline=False)
        embed.set_footer(text="Modmail")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        if not db.servers.find_one({'_id': ctx.guild.id}):
            category = await ctx.guild.create_category(name="Tickets")
            await category.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
            await category.set_permissions(ctx.guild.get_role(self.staff), read_messages=True, send_messages=True)
            db.servers.insert_one({'_id': self.guild, 'category': category.id})
            embed = discord.Embed(title="Setup", description=f"{ctx.author.mention} has setup Modmail.", color=0x00ff00)
            embed.set_footer(text="Modmail")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Setup Complete", description=f"The server {ctx.guild.name} has already been setup.", color=0x00ff00)
            embed.set_footer(text="Modmail")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx):
        try:
            embed = discord.Embed(title="Reset", description="The server was reset and all the db data has been deleted", color=0x00ff00)
            embed.set_footer(text="Modmail")
            await ctx.send(embed=embed)
            db.servers.delete_one({'_id': ctx.guild.id})
        except:
            embed = discord.Embed(title="Error:x:",
            description="The server is not setup.", color=discord.Color.red())
            embed.set_footer(text="Modmail")
            await ctx.send(embed=embed)
            
async def setup(bot):
    await bot.add_cog(Modmail(bot))
    # add slash commands
    print("Modmail is ready.")
