import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import requests

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

bot.run(TOKEN)