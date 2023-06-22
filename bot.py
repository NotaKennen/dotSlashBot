from statistics import mode
import discord
from discord.ext import commands
from compiler import compile
import threading
from queue import Queue

import os
import shutil

print("----------------------------------------------")

def runprogram(filename, author, mode):
    if mode != "temp" and mode != "permanent":
        raise SyntaxError("Failure in code")
    
    # Ready program for execution
    if mode == "permanent":
        with open(f"Saved programs/{author}/{filename}", 'r') as f:
            program = f.read()
    elif mode == "temp":
        with open(f"temp programs/{author}/{filename}", 'r') as f:
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

@bot.command(brief="Learn SlashScript here!")
async def documentation(ctx):
    await ctx.send("Coming soon")

@bot.command(brief="Upload programs to use for later")
async def upload_program(ctx, name=None): 
    try:
        for attachment in ctx.message.attachments:
            await attachment.save(attachment.filename)
            filename = attachment.filename
    except Exception as e:
        await ctx.send(f"There was an error uploading the program (Most likely you forgot to attach it)\n\n{e}")
        return
    
    # Checks if a name was input
    if name is None:
        name = filename
    else:
        os.rename(filename, f"{name}.txt")
        name += ".txt"

    if not os.path.exists(f"Saved programs/{ctx.author.id}"):
        os.makedirs(f"Saved programs/{ctx.author.id}")
    
    shutil.move(name, f"Saved programs/{ctx.author.id}/{name}")
    await ctx.send("The program has been saved! You can use it via ./program <program name>")
    
@bot.command(brief="Run a program you have saved")
async def program(ctx, name: str=None):
    # Only ./program (or ./program self)
    if name is None:
        if not os.path.exists(f"Saved programs/{ctx.author.id}"):
            await ctx.send("You don't have any programs")
            return
        programstring = ""
        programlist = os.listdir(f'Saved programs/{ctx.author.id}')
        for i in programlist:
            programstring += i + "\n"
        await ctx.send(f"You have saved the following programs:\n\n{programstring}\nYou can these programs with ./program <program name>")

    # ./program (name) <program name>
    else:
        if os.path.exists(f"Saved programs/{ctx.author.id}/{name}"):
            response = runprogram(name, ctx.author.id, "permanent")
            await ctx.send(response[1])
        else:
            await ctx.send("The program does not exist")
            return
            
@bot.command(brief="Run a program without saving it")
async def run_file(ctx):
    # Get file from user
    try:
        for attachment in ctx.message.attachments:
            await attachment.save(attachment.filename)
            filename = attachment.filename
            if not os.path.exists(f"temp programs/{ctx.author.id}"):
                os.makedirs(f"temp programs/{ctx.author.id}")
            shutil.move(filename, f"temp programs/{ctx.author.id}/{filename}")
    except Exception as e:
        await ctx.send(e)
        return

    try:
        response = runprogram(filename, ctx.author.id, "temp")
        await ctx.send(response[1]) # Send response
        os.remove(f"temp programs/{ctx.author.id}/{filename}") # Remove file
    except Exception as e:
        await ctx.send(f"The bot had an issue running the program, please try again later\n\n{e}")

####################################################

with open("token.txt" , 'r') as f:
    token = f.read()

bot.run(token)