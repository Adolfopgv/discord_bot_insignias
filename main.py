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
INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True

BOT = commands.Bot(command_prefix="$", intents=INTENTS)

# Commands
@BOT.command()
async def ranking(ctx):
    member_names = []

    for member in ctx.guild.members:
        if not member.bot:
            member_names.append(member.name)   

    await ctx.send(member_names)
    
@BOT.command()
async def insignias(ctx, arg: str = ""):
    insignias_rows = WORKSHEET_INSIGNIAS.get_all_values()
    insignias_names = [row[0].strip() for row in insignias_rows[1:]]

    if arg != "":
        member_rows = WORKSHEET_MIEMBROS.get_all_values()
        
        member_names = [row[1].strip() for row in member_rows[1:]]
        member_insignias = [row[2].strip() for row in member_rows[1:]]
        
        if arg in member_names:
            # Imprimir las insignias de un miembro
            print(arg)
        
        elif arg in insignias_names:
            # Imprimir todo sobre una insignia
            print(arg)
    else:
        # Solo imprimir las insignias
        table = "Nombre Insignia\n---------------\n"
        for row in insignias_names:
            table += f"{row}\n"

        await ctx.send(table)

        
@BOT.command()
async def darinsignia(ctx, *arg):
    member_rows = WORKSHEET_MIEMBROS.get_all_values()
    insignias_rows = WORKSHEET_INSIGNIAS.get_all_values()
    
    member_names = [row[1].strip() for row in member_rows[1:]]
    member_insignias = [row[2].strip() for row in member_rows[1:]]
    insignias_names = [row[0].strip() for row in insignias_rows[1:]]
    
    if arg[0].strip() not in insignias_names and arg[1].strip() not in member_names:
        await ctx.send("No existe esa insignia o usuario")
    else:
        for index, member_name in enumerate(member_names):
            if member_name.strip() == arg[1].strip():
                insignias = [member_insignias[index]]
                if arg[0].strip() not in insignias:
                    insignias.append(arg[0])
                    if (insignias[0] == ""):
                        insignias.pop(0)
                    insignias_str = ", ".join(insignias)
                    WORKSHEET_MIEMBROS.update_cell(index + 2, 3, insignias_str)
                    await ctx.send(f"Insignia {arg[0]} dada a {arg[1]}")
                    break
                else:
                    await ctx.send(f"{arg[1]} ya tiene la insignia {arg[0]}")
                    break

@BOT.command()
async def crearinsignia(ctx, *arg):
    print("Insignia creada")

# Events
@BOT.event
async def on_message(message):
    await BOT.process_commands(message)
    if message.content.startswith("$crearinsignia"):
        res = message.content.split(" ")[1:]
        res.append(message.attachments[0].url)
        WORKSHEET_INSIGNIAS.append_row(res)
        await message.channel.send("Insignia creada")

@BOT.event
async def on_ready():
    print(f"Logged in as {BOT.user.name}")
    print("Bot is ready to use")
    
    guild = BOT.get_guild(GUILD_ID)
    if guild == None:
        guild = await BOT.fetch_guild(GUILD_ID) # if guild not in cache
    
    members = [member async for member in guild.fetch_members(limit=None)]
    rows = WORKSHEET_MIEMBROS.get_all_values()
    
    db_member_ids = [row[0].strip() for row in rows[1:]] if rows[1:] else []
    users = []
    members_in_server_ids = []
    
    for member in members:
        if not member.bot and str(member.id) != str(DEV_ID):
            members_in_server_ids.append(str(member.id).strip())
            if str(member.id).strip() not in db_member_ids:
                users.append([str(member.id), member.name])
                print(f"New member: {member.name} ID: {member.id}")

    if users:
        WORKSHEET_MIEMBROS.append_rows(users)
        
    rows_to_delete = [
        index for index, row in enumerate(rows[1:], start=2)
        if row[0].strip() not in members_in_server_ids
    ]
    
    for index in reversed(rows_to_delete):
        WORKSHEET_MIEMBROS.delete_rows(index)
        print(f"Deleted row: {index}")
    
@BOT.event
async def on_member_join(member):
    if not member.bot:
        print(f"New member joined: Name: {member.name} ID: {member.id}")
        WORKSHEET_MIEMBROS.append_row([str(member.id), member.name])
    
@BOT.event
async def on_member_remove(user):
    if not user.bot:
        print(f"Member left: Name: {user} ID: {user.id}")
        rows = WORKSHEET_MIEMBROS.get_all_values()
        
        for index, row in enumerate(rows[1:] , start=2):
            if (row[0].strip() == str(user.id).strip()):
                WORKSHEET_MIEMBROS.delete_rows(index)
                print(f"Deleted row: {index}")
                break

BOT.run(TOKEN)