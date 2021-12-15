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
from discord_webhook import DiscordWebhook

#you shouldnt touch any of this ngl 

bot = commands.Bot(command_prefix = '>', activity=discord.Game(name="Helping people (I think :p)"))
TOKEN = os.getenv('BOT_TOKEN')
guild = bot.get_guild(919710676056965120)
DATABASE_URL = os.environ['DATABASE_URL']
bot.db = Database()
startupWebhook = os.getenv('STARTUP')
roleList = []

#triggers that would cause it to check for FAQs
embedTriggers = ["revo release","revo be released","hemera be restocked", "hemera stock", "brexit", "documentation", "refund", "support", "help", "beta"]

class discordEmbed: #discord embed properties, condensed into classes and objects for easy indexing
  def __init__(self, key, title, url, description, image):
    self.key = key #the name of the embed internally
    self.title = title #top text of the embed
    self.url = url #url where you are sent when you click the title
    self.description = description #big paragraph of text
    self.image = image #link to image that shows under the description

    #none of these are necessart and can be blank
    #remember to use the newline character (\n) to insert an enter
    #add "authorName" where you want the bot to put the name of the sender


revoEmbed = discordEmbed("revo",
                         "Revo will ship early january, authorName!",
                         "https://e3d-online.com/blogs/news/rapidchangerevo",
                         "Read more about the Revo(lution) here: \n https://e3d-online.com/blogs/news/rapidchangerevo",
                         "https://cdn.shopify.com/s/files/1/0259/1948/8059/files/revo-micro_600x600.png?v=1632850458")

hemerestockEmbed = discordEmbed("hemerestock",
                                "It is restocked!",
                                "https://e3d-online.com/blogs/news/hemera-back-in-stock",
                                "Buy one today!\nhttps://e3d-online.com/blogs/news/hemera-back-in-stock",
                                "https://cdn.shopify.com/s/files/1/0259/1948/8059/articles/Hemera_reflection_front_tiled_16_9_6097ee2d-0c83-45fd-95a7-1a68a0fb07ac_350x.jpg?v=1610971099")

brexitEmbed = discordEmbed("brexit",
                           "Good question.",
                           "https://e3d-online.com/blogs/news/brexit",
                           "Here's what we know:\nhttps://e3d-online.com/blogs/news/brexit\nIf you'd like to get an estimate of shipping and customs costs before buying something, please open a ticket with customer support who can help you further:\nhttps://e3d-online.com/pages/contact-us",
                           "https://cdn.shopify.com/s/files/1/0259/1948/8059/articles/BREXIT_350x.jpg?v=1612267837")

docuEmbed = discordEmbed("docu",
                         "Where can I find documentation?",
                         "https://e3d-online.zendesk.com/hc/en-us",
                         "Latest documentation: https://e3d-online.zendesk.com/hc/en-us\nLegacy documentation: https://e3d-online.dozuki.com/c/Root\n(We're in the process of moving everything over to ZenDesk. Some info can still be found on Dozuki)\nDocumentation can be found pinned under each product help channel respectively. If you think something is missing, feel free to @ any of our team.",
                         "https://theme.zdassets.com/theme_assets/1210792/c64cdacf7096bc8e38724270bdf1680060b86893.svg")

suppEmbed = discordEmbed("support",
                         "I'm having issues with my printer, what should I do?", 
                         "https://e3d-online.zendesk.com/hc/en-us",
                         "Write a message in one of the help channels relating to the E3D product you're having issues with, and we'll be happy to help you out.\nIf it's related to purchase, refunds etc. visit https://e3d-online.com/pages/contact-us, open a ticket and the E3D support team will be happy to help.",
                         "https://theme.zdassets.com/theme_assets/1210792/c64cdacf7096bc8e38724270bdf1680060b86893.svg")

betaEmbed = discordEmbed("beta",
                         "Is there a channel to discuss beta products here?",
                         "https://e3d-online.zendesk.com/hc/en-us/requests/new?ticket_form_id=360000243458",
                         "No, sorry.\nWe have dedicated forums for beta programs as we need to track all information about beta products in once place. Please use that forum to discuss anything in the beta program.\nIf you'd like to join the beta program, you can do it here: https://e3d-online.zendesk.com/hc/en-us/requests/new?ticket_form_id=360000243458",
                         "")

#dont mess with the on ready event or the on connect event

@bot.event
async def on_ready():
    bot.guild = bot.get_guild(919710676056965120)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('Helping people (I think :p)'))
    print("--------------------") 
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('--------------------')
    webhook = DiscordWebhook(url=startupWebhook, rate_limit_retry=True, content=f'-------------------- \n Logged in as \n {bot.user.name} \n {bot.user.id} \n --------------------')
    response = webhook.execute()

@bot.listen()
async def on_connect():
    await bot.db.setup()
    print("database loaded")

# function to build the embed according to the trigger, moved it to a function to keep it tidier
def acquireEmbed(message, authorName):

    if "revo" and "release" in message:
        embedTitle = revoEmbed.title.replace("authorName", authorName) #insert authorName where you want the bot to place the name of the person who asked
        embedURL = revoEmbed.url
        embedDescription = revoEmbed.description
        embedImage = revoEmbed.image

    if "hemera" and "stock" in message:
        embedTitle = hemerestockEmbed.title
        embedURL = hemerestockEmbed.url
        embedDescription = hemerestockEmbed.description
        embedImage = hemerestockEmbed.image
    
    if "brexit" in message:
        embedTitle = brexitEmbed.title
        embedURL = brexitEmbed.url
        embedDescription = brexitEmbed.description
        embedImage = brexitEmbed.image
    
    if "documentation" in message:
        embedTitle = docuEmbed.title
        embedURL = docuEmbed.url
        embedDescription = docuEmbed.description
        embedImage = docuEmbed.image

    #if "support" or "help" in message:
        #embedTitle = suppEmbed.title
        #embedURL = suppEmbed.url
        #embedDescription = suppEmbed.description
        #embedImage = suppEmbed.image
    
    if "beta" in message:
        embedTitle = betaEmbed.title
        embedURL = betaEmbed.url
        embedDescription = betaEmbed.description
        embedImage = betaEmbed.image

    embed = discord.Embed(title= embedTitle, url= embedURL ,description = embedDescription)
    embed.set_image(url= embedImage)
    return embed 

#here is where the magic happens
@bot.listen()
async def on_message(message):
    if message.author.bot:
        return 
    if str(message.channel.type) == "private":
        await message.channel.send("Hey there! I dont answer to dms yet.")
        return
    if message.author == bot.user:
        return
    user = await bot.db.get_user(message.author.id)
    for x in embedTriggers:
        if x in message.content:
            await message.channel.send(embed=acquireEmbed(message.content, message.author.name))
       
#ignore the leaderboard, not usable yet since there is no xp rewards
@bot.command()
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

#leave this guy alone unless you want to add a feature to it
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

bot.run(TOKEN) #starts the nuclear reactor