import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import requests
import gspread

# Google Sheets config
SERVICE_ACCOUNT = gspread.service_account(filename="discord-bot-insignias-2507749f19b3.json")
SHEET = SERVICE_ACCOUNT.open("bot_insignias")

# Google Sheets worksheets
WORKSHEET_MIEMBROS = SHEET.worksheet("miembros")
WORKSHEET_INSIGNIAS = SHEET.worksheet("insignias")

# Environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
DEV_ID = os.getenv("DEV_ID")

# Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

# Commands
@bot.command()
async def ranking(ctx):
    member_names = []
    for member in ctx.guild.members:
        if not member.bot:
            member_names.append(member.name)   
    await ctx.send(member_names)
    
@bot.command()
async def insignias(ctx, arg):
    await ctx.send(arg)
    
@bot.command()
async def darinsignia(ctx, arg):
    await ctx.send(arg)

# Events
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print("Bot is ready to use")
    
    guild = bot.get_guild(GUILD_ID)
    if guild == None:
        guild = await bot.fetch_guild(GUILD_ID) # if guild not in cache
    
    members = [member async for member in guild.fetch_members(limit=None)]
    users = []
    for member in members:
        if not member.bot and str(member.id) not in [row[0] for row in WORKSHEET_MIEMBROS.get_all_values()] and str(member.id) != str(DEV_ID):
            users.append([str(member.id), member.name, ""])
    
    if users:
        WORKSHEET_MIEMBROS.append_rows(users)
    
@bot.event
async def on_member_join(member):
    if not member.bot:
        print(f"New member joined: Name: {member.name} ID: {member.id}")
        WORKSHEET_MIEMBROS.append_row([str(member.id), member.name, ""])
    
@bot.event
async def on_member_remove(user):
    print(f"Member left: Name: {user} ID: {user.id}")
    rows = WORKSHEET_MIEMBROS.get_all_values()
    
    for index, row in enumerate(rows[1:] , start=2):
        if (row[0].strip() == str(user.id).strip()):
            WORKSHEET_MIEMBROS.delete_rows(index)
            print(f"Deleted row: {index}")
            break

bot.run(TOKEN)