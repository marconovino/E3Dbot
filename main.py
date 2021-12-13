import discord
import math
import random
import asyncio
import logging
import os
import datetime
from discord.ext import commands, tasks
import re
from discord import Intents
from db import Database
from typing import Text, Tuple
from math import sqrt
from discord.utils import get

bot = commands.Bot(command_prefix = '>', activity=discord.Game(name="Helping people (I think :p)"))
TOKEN = os.getenv('BOT_TOKEN')
guild = bot.get_guild(919710676056965120)
DATABASE_URL = os.environ['DATABASE_URL']
bot.db = Database()
roleList = []
revoreleasetriggers = ["REVO RELEASE"]

@bot.event
async def on_ready():
    bot.guild = bot.get_guild(919710676056965120)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('Helping people (I think :p)'))
    print("--------------------")
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('--------------------')

@bot.listen()
async def on_connect():
    await bot.db.setup()
    print("database loaded")

@bot.listen()
async def on_message(message):
    if str(message.channel.type) == "private":
        await message.channel.send("Hey there! I dont answer to dms yet.")
        return
    if message.author.bot:
        return 
    if message.author == bot.user:
        return
    user = await bot.db.get_user(message.author.id)
    if any(re.search(trg,message.content.upper()) != None for trg in revoreleasetriggers):
        embed = discord.Embed(title=f"Revo will ship early january, {message.author.name}!", url="https://e3d-online.com/blogs/news/rapidchangerevo",description = f"Read more here: https://e3d-online.com/blogs/news/rapidchangerevo")

async def leaderboard(ctx):
    usrnum = 1
    embed = discord.Embed(
        title="XP leaderboard", description="", color=0x0c0f27)
    users = await bot.db.get_leaderboard()
    for x in users:
        user = await bot.fetch_user(x["id"])
        username = str(user)
        embed.add_field(name=f"{usrnum}. {username}", value=f'XP: {x["xp"]}',inline=False)
        usrnum = usrnum + 1
    await ctx.send(embed=embed)

@bot.command(aliases=["whois"])
async def userinfo(ctx, member: discord.Member = None):
    if not member:
        member = ctx.message.author
    roles = [role for role in member.roles]
    embed = discord.Embed(colour=discord.Colour.purple(), timestamp=ctx.message.created_at,
                          title=f"User Info - {member}")
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}")

    embed.add_field(name="ID:", value=member.id)
    embed.add_field(name="Display Name:", value=member.display_name)

    embed.add_field(name="Created Account On:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name="Joined Server On:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

    embed.add_field(name="Roles:", value="".join([role.mention for role in roles]))
    embed.add_field(name="Highest Role:", value=member.top_role.mention)
    print(member.top_role.mention)
    await ctx.send(embed=embed)

@bot.command()
async def unban(ctx, member: discord.Member = None):
    member.unban()

@bot.event
async def on_command_error(ctx, error):
    logging.error(f'Error on command {ctx.invoked_with}, {error}')
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="Error!",
                              description=f"The command `{ctx.invoked_with}` was not found! We suggest you do `>help` to see all of the commands",
                              colour=0xe73c24)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRole):
        embed = discord.Embed(title="Error!",
                              description=f"You don't have permission to execute `{ctx.invoked_with}`.",
                              colour=0xe73c24)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error!",
                              description=f"`{error}`",
                              colour=0xe73c24)
        await ctx.send(embed=embed)
        raise error



bot.run(TOKEN)