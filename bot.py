Custos by Alex Goldsbrough

import os
import asyncio
import discord
from discord.ext import commands

# ---- Intents ----
intents = discord.Intents.default()
intents.message_content = True   # required for prefix commands
intents.members = True           # needed for reliable member resolution in kick/ban

# ---- Bot ----
bot = commands.Bot(
    command_prefix='-',
    intents=intents,
    status=discord.Status.online,
    activity=discord.Game(name="do -help to Help!")
)
bot.remove_command('help')

# ---- Events ----
@bot.event
async def on_ready():
    print("I am up and running!")

# ---- Help ----
@bot.command()
async def help(ctx: commands.Context):
    embed = discord.Embed(colour=discord.Color.red())
    embed.set_author(name="Help Menu")
    embed.add_field(name="-help", value="Show all commands.", inline=False)
    embed.add_field(name="-ping", value="Check the bot's latency.", inline=False)
    embed.add_field(name="-purge [amount]", value="Delete the last N messages.", inline=False)
    embed.add_field(name="-ban [@member]", value="Ban a user.", inline=False)
    embed.add_field(name="-kick [@member]", value="Kick a user.", inline=False)

    try:
        await ctx.author.send(embed=embed)
        await ctx.send("**Message sent to your DMs.**")
    except discord.Forbidden:
        await ctx.send("**I can't DM you. Enable DMs from server members.**")

# ---- Ping ----
@bot.command()
async def ping(ctx: commands.Context):
    ping_ms = round(bot.latency * 1000)
    await ctx.send(f"My ping is **{ping_ms}ms**")

# ---- Purge ----
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx: commands.Context, amount: int):
    if amount < 1:
        await ctx.send("**Amount must be at least 1.**")
        return
    # Bulk delete ignores messages older than 14 days
    deleted = await ctx.channel.purge(limit=amount, bulk=True)
    msg = await ctx.send(embed=discord.Embed(
        color=discord.Color.green(),
        description=f"I have purged **{len(deleted)}** message(s)."
    ))
    await asyncio.sleep(2)
    try:
        await msg.delete()
    except discord.NotFound:
        pass

@purge.error
async def purge_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=discord.Embed(
            color=discord.Color.red(),
            description="You do not have permission to purge messages."
        ))
    else:
        await ctx.send("**Unable to purge messages.**")

# ---- Kick ----
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx: commands.Context, user: discord.Member | None = None, *, reason: str | None = None):
    if user is None:
        await ctx.send("**Please mention a user.**")
        return
    try:
        await user.kick(reason=reason or f"Kicked by {ctx.author}")
        await ctx.send(f"**I have chased {user.mention} away. Cya!**")
    except discord.Forbidden:
        await ctx.send("**I cannot kick that user. Check my role position and permissions.**")

# ---- Ban ----
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx: commands.Context, user: discord.Member | None = None, *, reason: str | None = None):
    if user is None:
        await ctx.send("**Please mention a user.**")
        return
    try:
        await user.ban(reason=reason or f"Banned by {ctx.author}")
        await ctx.send(f"**I have jailed {user.mention}. Cya!**")
    except discord.Forbidden:
        await ctx.send("**I cannot ban that user. Check my role position and permissions.**")

# ---- Entry point ----
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN") or "TOKEN_HERE"
    bot.run(token)
