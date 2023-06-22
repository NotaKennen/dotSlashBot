from statistics import mode
import discord
from discord.ext import commands
from compiler import compile
import threading
from queue import Queue

import os
import shutil

print("----------------------------------------------")

def runprogram(filename, author):
    # Ready program for execution
    with open(f"Saved programs/{author}/{filename}", 'r') as f:
        program = f.read()
    program = program.split('\n')

    try: # Execution
        queue = Queue()
        programthread = threading.Thread(name=filename, target=compile, args=(program, queue)) # make thread
        programthread.start() # Run program
        programthread.join() # Wait for program to finish
        response = queue.get() # get response
        
        # Response fancycating
        strresponse = "" # Make a string
        for i in response: # No lists
            strresponse += str(i)
            strresponse += "\n\n"

        return (True, strresponse)
    except Exception as e: # Failure catching
        return (False, f"The program had an issue:\n{e}")


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='./',intents=intents)

@bot.event
async def on_ready():
    botactivity = discord.Activity(type=discord.ActivityType.watching, name="you code")
    await bot.change_presence(activity=botactivity, status=discord.Status.online)
    print('Logged in as')
    print(bot.user.name)
    print('----------------------------------------------')

@bot.command()
async def upload_file(ctx, name=None): 
    try: #TODO: Ask for public/hidden/private program
        for attachment in ctx.message.attachments:
            await attachment.save(attachment.filename)
            filename = attachment.filename
    except Exception as e:
        await ctx.send(e)
        return
    
    # Checks if a name was input
    if name is None:
        name = filename
    else:
        os.rename(filename, f"{name}.txt")

    if not os.path.exists("Saved programs"):
        os.makedirs("Saved programs")
    if not os.path.exists(f"Saved programs/{ctx.author.id}"):
        os.makedirs(f"Saved programs/{ctx.author.id}")
    
    shutil.move(name, f"Saved programs/{ctx.author.id}/{name}")
    await ctx.send("The program has been saved! You can use it via ./program <program name>")
    
@bot.command()
async def program(ctx, name: str=None):
    if name is None:
        await ctx.send(f"You have saved the following programs:\n{''.join(os.listdir(f'Saved programs/{ctx.author.id}'))}\nYou can these programs with ./program <program name>")
    elif name.lower() == "global":
        await ctx.send("**TODO** send all public programs") #TODO: send programs
    else:
        if os.path.exists(f"Saved programs/{ctx.author.id}/{name}"):
            response = runprogram(name, ctx.author.id)
            await ctx.send(response[1])
        else:
            await ctx.send("The program does not exist")
            return
            
@bot.command()
async def run_file(ctx):
    # Get file from user
    try:
        for attachment in ctx.message.attachments:
            await attachment.save(attachment.filename)
            filename = attachment.filename
    except Exception as e:
        await ctx.send(e)
        return

    try:
        response = runprogram(filename, ctx.author.id)
        await ctx.send(response[1]) # Send response
    except Exception as e:
        await ctx.send(f"The bot had an issue running the program, please try again later\n\n{e}")

####################################################

with open("token.txt" , 'r') as f:
    token = f.read()

bot.run(token)