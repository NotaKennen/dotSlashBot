from statistics import mode
import discord
from discord.ext import commands
from compiler import compile
import threading
from queue import Queue
import asyncio

import os
import shutil

print("----------------------------------------------")

def runprogram(filename, author, mode):
    if mode != "temp" and mode != "permanent":
        raise SyntaxError("Failure in code")
    
    # Ready program for execution
    if mode == "permanent":
        with open(f"Saved programs/{author}/{filename}", 'r') as f:
            code = f.read()
    elif mode == "temp":
        with open(f"temp programs/{author}/{filename}", 'r') as f:
            code = f.read()
    code = code.split('\n')

    try: # Execution
        queue = Queue()
        programthread = threading.Thread(name=filename, target=compile, args=(code, queue)) # make thread
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

@bot.command(brief="Run a single line of code")
async def run_line(ctx, *, line: str=None):
    if line is None:
        await ctx.send("Usage: ./run_line (code)")
        return
    line = line.split("\n")
    
    queue = Queue()
    programthread = threading.Thread(name=ctx.author, target=compile, args=(line, queue)) # make thread
    programthread.start() # Run program
    programthread.join() # Wait for program to finish
    response = queue.get() # get response
    
    # Response fancycating
    strresponse = "" # Make a string
    for i in response: # No lists
        strresponse += str(i)
        strresponse += "\n\n"

    await ctx.send(strresponse)

@bot.command(brief="Learn about SlashScript here!")
async def documentation(ctx):
    contents = ["Table of contents:\n\n2. SlashScript introduction\n3. Basic syntax\n4. Commands\n5. Respond\n6. Var\n7. Math\n8. If\n9. Goto\n10. Exit\n11. Sources",
                'SlashScript is a small programming "language", or a script as I prefer to call it. The language isnt too big as its not meant to be used for bigger projects, but you can make quite a bit of fun stuff with it.',
                "SlashScript uses a lot of spaces ~~~for smart interactions with users~~ because the developer is too lazy to code proper compiling. Because of this, parenthesis and quotes aren't seen too often.",
                "SlashScript has a total of 6 commands (as of 22/06/2023), these are: Respond, Var, Math, If, Goto and Exit. Each of these commands has a documentation page, feel free to check them.",
                "Respond is the equivalent of Print in python, the syntax is 'respond [message]', the message will appear at the end of execution. If you want to 'print' a variable, you need to use 'respond VAR [variable]', caps is necessary.",
                "Var works for assigning variables. SlashScript has 3 variable types: int/float, str and bool. The syntax is: 'var [name] [value]'. The type is calculated automatically.",
                "The math command can do math and turn it into a variable, usage is: 'math [variable] [value1] [operator] [value2]'. The operator can be: +, -, *, /, %",
                "If is for conditionals. The syntax is: 'if [variable] [operator] [variable] [goto] <elsegoto>'. Goto means the line to go to if the condition is true. Elsegoto means the line to go to if the condition is false, and is optional. The operators are *exactly* like python's.",
                "Goto is for jumping lines, the syntax is 'goto [line]'",
                "Exit is as simple as it gets, it exits the program. The syntax is 'exit'",
                "You can find both the bot's and the compiler's source code here: https://github.com/NotaKennen/dotSlashBot. You can DM the developer (Memarios_) with extra questions or ideas."]
    pages = 11
    cur_page = 1
    message = await ctx.send(f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
    # getting the message object for editing and reacting

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
        # This makes sure nobody except the command sender can interact with the "menu"

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
            # waiting for a reaction to be added - times out after x seconds, 60 in this
            # example

            if str(reaction.emoji) == "▶️" and cur_page != pages:
                cur_page += 1
                await message.edit(content=f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                await message.edit(content=f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
                await message.remove_reaction(reaction, user)

            else:
                await message.remove_reaction(reaction, user)
                # removes reactions if the user tries to go forward on the last page or
                # backwards on the first page
        except asyncio.TimeoutError:
            await message.delete()
            break
            # ending the loop if user doesn't react after x seconds

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
    
@bot.command(brief="Delete a program you have saved")
async def delete_program(ctx, *, name=None):
    if name is None:
        await ctx.send("You need to specify a program name")
        return
    if os.path.exists(f"Saved programs/{ctx.author.id}/{name}"):
        os.remove(f"Saved programs/{ctx.author.id}/{name}")
        await ctx.send("The program has been deleted")
    else:
        await ctx.send("The program does not exist")
        return

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