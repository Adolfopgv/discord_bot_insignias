import os
import webserver
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import requests
import gspread
import re
import shlex

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
GUILD_OWNER_ID = os.getenv("GUILD_OWNER_ID")

# Intents
INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True

BOT = commands.Bot(command_prefix="$", intents=INTENTS)
BOT.remove_command("help")

# Functions
def clean_member_rows(member_rows):
    member_names = []
    member_insignias = []
    clean_member_names = []
    clean_member_insignias = []
        
    for row in member_rows[1:]:
        clean_row1 = re.sub(r"[^\w\s]", "", row[1]).strip().lower()
        clean_row2 = re.sub(r"[^\w\s]", "", row[2]).strip().lower()
        member_names.append(row[1].strip())
        member_insignias.append(row[2].strip())
        clean_member_names.append(clean_row1)
        clean_member_insignias.append(clean_row2)
    
    return member_names, member_insignias, clean_member_names, clean_member_insignias

def clean_insignias_rows(insignias_rows):
    insignias_names = []
    clean_insignias_names = []
    
    for row in insignias_rows[1:]:
        clean_row = re.sub(r"[^\w\s]", "", row[0]).strip().lower()
        clean_insignias_names.append(clean_row)
        insignias_names.append(row[0].strip())
    
    return insignias_names, clean_insignias_names

# Commands
@BOT.command()
async def help(ctx):
    help_message = "# ACLARACIONES:\n"
    help_message += "```\n"
    help_message += " - Los comandos comienzan con el símbolo \"$\".\n"
    help_message += " - Para escribir argumentos en un comando, separa cada argumento con un espacio.\n"
    help_message += "Ejemplo: $insignias \"Nomura cabron\"\n"
    help_message += "         $insignias laxarc\n\n"
    help_message += " - Para escribir un nombre, tanto de un miembro como de una insignia, con ESPACIOS, se debe de escribir entre COMILLAS (\" \").\n"
    help_message += "Ejemplo: Una insignia llamada Nomura cabron se debe de escribir entre comillas como \"Nomura cabron\".\n"
    help_message += "Lo mismo implica para el nombre de un miembro.\n\n"
    help_message += " - No hace falta escribir un emoticono en el caso de que algún miembro o insignia lo tenga en el nombre.\n"
    help_message += " - No hace falta preocuparse por mayúsculas o minúsculas en el nombre de un miembro o insignia.\n"
    help_message += " - Cualquier error o algo que penseis que se pueda mejorar, escribid a @Adolfo\n"
    help_message += " - Por último, ¡Disfrutad del bot! :)\n"
    help_message += "```\n"

    help_message += "# Comandos\n"
    help_message += "```\n"
    help_message += "$ranking -- Imprime al top 5 de los miembros con más insignias\n\n"
        
    help_message += "$insignias [nombre de la insignia] -- Imprime toda la información de una insignia\n"
    help_message += " - Ejemplo: $insignias \"Nomura cabron\" o $insignias urasawa\n\n"
    help_message += "$insignias [nombre de un miembro] -- Imprime todas las insignias de un miembro\n"
    help_message += " - Ejemplo: $insignias laxarc\n\n"
    help_message += "$insignias -- Imprime todas las insignias\n\n"

    if str(ctx.author.id).strip() == str(GUILD_OWNER_ID).strip():
        help_message += "ADMINISTRADOR\n"
        help_message += "-------------\n"
        help_message += "$darinsignia [nombre de la insignia] [nombre del miembro]\n"
        help_message += " - Ejemplo: $darinsignia \"Nomura cabron\" laxarc\n\n"
        help_message += "$crearinsignia [nombre de la insignia] [logro de la insignia] imagen adjunta\n"
        help_message += " - Ejemplo: $crearinsignia \"Nomura cabron\" \"Leer la historia entera de KH y entenderla\" adjuntar imagen con el + de discord\n\n"
    help_message += "```"
    await ctx.send(help_message)

@BOT.command()
async def ranking(ctx):
    # Imprimir los miembros ordenados por número de insignias
    member_rows = WORKSHEET_MIEMBROS.get_all_values()
    member_names = []
    member_insignias = []
        
    for row in member_rows[1:]:
        member_names.append(row[1].strip())
        member_insignias.append(row[2].strip())
    
    member_name_insignias = [
        (name, insignias, len(insignias.split(", ")) if insignias else 0)
        for name, insignias in zip(member_names, member_insignias)
    ]
    
    sort_insignias = sorted(member_name_insignias, key=lambda x: x[2], reverse=True)
    emojis = [":first_place:", ":second_place:", ":third_place:", ":four:", ":five:"]
    
    table = f"# Ranking\n"
    for index, name_insignia in enumerate(sort_insignias[:5], start=1) :
        if name_insignia[1] != "":
            table += f"{emojis[index - 1]} {name_insignia[0]} | {name_insignia[1]}\n"
    
    await ctx.send(table)
            
@BOT.command()
async def insignias(ctx, arg: str = ""):
    parsed_args = shlex.split(arg)
    insignias_rows = WORKSHEET_INSIGNIAS.get_all_values()
    insignias_names, clean_insignias_names = clean_insignias_rows(insignias_rows)

    if parsed_args:
        clean_arg = re.sub(r"[^\w\s]", "", " ".join(parsed_args)).strip().lower()
        
        member_rows = WORKSHEET_MIEMBROS.get_all_values()
        member_names, member_insignias, clean_member_names, clean_member_insignias = clean_member_rows(member_rows)
            
        if clean_arg in clean_member_names:
            # Imprimir las insignias de un miembro
            for index, member in enumerate(member_rows[1:]):
                if clean_arg == clean_member_names[index]:
                    if member[2].strip() != "":
                        table = f"# {member[1].strip()}\n---------------\n"
                        insignias = member[2].replace(", ", "\n")
                        table += f"{insignias}\n"
                        await ctx.send(table)
                        break
                    else:
                        await ctx.send(f"{member[1].strip()} no tiene insignias")
                        break
                
        elif clean_arg in clean_insignias_names:
            # Imprimir todo sobre una insignia
            for index, insignia in enumerate(insignias_rows[1:]):
                if clean_arg == clean_insignias_names[index]:
                    table = f"# {insignia[0].strip()}\n---------------\n"
                    table += f"{insignia[1].strip()}\n{insignia[2].strip()}"
                    await ctx.send(table)
                    break
                
        else:
            await ctx.send(f"No existe ninguna insignia o miembro llamado {arg}")
    else:
        # Solo imprimir las insignias
        table = "# Nombre Insignia\n---------------\n"
        for row in insignias_names:
            table += f"{row}\n"

        await ctx.send(table)

        
@BOT.command()
async def darinsignia(ctx, *, arg):
    if str(ctx.author.id).strip() == str(GUILD_OWNER_ID).strip():
        parsed_args = shlex.split(arg)
        
        if len(parsed_args) < 2:
            return await ctx.send("Debes proporcionar al menos dos argumentos: la insignia y el nombre del usuario.")
        
        arg_insignia = parsed_args[0]
        arg_member = parsed_args[1]
        
        member_rows = WORKSHEET_MIEMBROS.get_all_values()
        insignias_rows = WORKSHEET_INSIGNIAS.get_all_values()
            
        member_names, member_insignias, clean_member_names, clean_member_insignias = clean_member_rows(member_rows)
        insignias_names, clean_insignias_names = clean_insignias_rows(insignias_rows)
            
        clean_arg_insignias = re.sub(r"[^\w\s]", "", arg_insignia).strip().lower()
        clean_arg_member = re.sub(r"[^\w\s]", "", arg_member).strip().lower()
            
        if clean_arg_insignias not in clean_insignias_names or clean_arg_member not in clean_member_names:
            return await ctx.send("No existe esa insignia o usuario.")
            
        for index, member_name in enumerate(member_names):
            if clean_member_names[index] == clean_arg_member:
                insignias = [member_insignias[index]]
                clean_insignias = [clean_member_insignias[index]]
                    
                if clean_arg_insignias not in clean_insignias:
                    insignias.append(arg_insignia)
                    if insignias[0] == "":
                        insignias.pop(0)
                    insignias_str = ", ".join(insignias)
                    WORKSHEET_MIEMBROS.update_cell(index + 2, 3, insignias_str)
                    return await ctx.send(f"Insignia '{arg_insignia}' dada a {arg_member}.")
                else:
                    return await ctx.send(f"{arg_member} ya tiene la insignia '{arg_insignia}'.")
    else:
        await ctx.send("Solo el propietario puede dar insignias.")

@BOT.command()
async def crearinsignia(ctx, *arg):
    if str(ctx.author.id).strip() == str(GUILD_OWNER_ID).strip():
        print("Insignia creada")
    else:
        print("Solo el propietario puede crear insignias")

# Events
@BOT.event
async def on_message(message):
    await BOT.process_commands(message)
    if message.author.bot:
        return
    
    if message.content.startswith("$crearinsignia"):
        if str(message.author.id).strip() != str(GUILD_OWNER_ID).strip():
            return await message.channel.send("Solo el propietario puede crear insignias")
        res = message.content[len("$crearinsignia "):]
        parsed_res = shlex.split(res)
        
        if not message.attachments:
                return await message.channel.send("Debes incluir un archivo adjunto para la insignia.")
            
        parsed_res.append(message.attachments[0].url)
        WORKSHEET_INSIGNIAS.append_row(parsed_res)
        return await message.channel.send("Insignia creada")

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

webserver.start_server()
BOT.run(TOKEN)