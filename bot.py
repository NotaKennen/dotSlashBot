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

def runprogram(ctx, filename, author, mode, arguments: str=None):
    """
    Runs a program in the compiler:

    Arguments:
     - Filename: the name of the file, the path is decided by "mode"
     - Author: the author is for the ID of the author (except in cc mode)
     - Mode: decides the path to the file
     - Arguments: arguments to use
    """
    if mode != "temp" and mode != "permanent" and mode != "custom":
        raise SyntaxError("Failure in code")
    
    ### Logic ###

    if ctx.message.author.guild_permissions.administrator:
        admin = True
    else:
        admin = False

    if arguments is None:
        arguments = [""]
    else:
        arguments = arguments.split(" ")

    ### Execution ###
    
    # Ready program for execution
    if mode == "permanent":
        with open(f"Saved programs/{author}/{filename}", 'r') as f:
            code = f.read()
    elif mode == "temp":
        with open(f"temp programs/{author}/{filename}", 'r') as f:
            code = f.read()
    elif mode == "custom":
        with open(f"Server commands/{ctx.guild.id}/{author}/{filename}.txt", "r") as f:
            code = f.read()

    code = code.split('\n')

    try: # Execution
        responsequeue = Queue()
        actionqueue = Queue()
        programthread = threading.Thread(name=filename, target=compile, args=(code, responsequeue, actionqueue, admin, arguments)) # make thread
        programthread.start() # Run program
        programthread.join() # Wait for program to finish
        response = responsequeue.get() # get response
        action = actionqueue.get()

        if response[0] == "ERROR LOG":
            return [False, f"The program had an issue:\n{response[1]}"]
        
        try:
            if action is not None:
                for i in action:
                    exec(i)
        except Exception as e:
            return [False, f"Something went wrong inside the discord commands, currently the error is unknown, but most likely is due to invalid arguments that weren't handled properly:\n\n {e}"]
        
        # Response fancycating
        strresponse = "" # Make a string
        for i in response: # No lists
            strresponse += str(i) # Add item to string
            strresponse += "\n\n" # Padding

        return (True, strresponse)
    except Exception as e: # Failure catching
        return (False, f"An internal issue happened:\n{e}")


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='./',intents=intents)

@bot.event
async def on_ready():
    botactivity = discord.Activity(type=discord.ActivityType.watching, name="you code [./]")
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

    if ctx.message.author.guild_permissions.administrator:
        admin = True
    else:
        admin = False
    
    queue = Queue()
    programthread = threading.Thread(name=ctx.author, target=compile, args=(line, queue, admin)) # make thread
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
    contents = ["Table of contents:\n\n2. SlashScript introduction\n3. Uploading programs\n4. Limitations and resources\n5. Basic syntax\n6. Commands\n7. Respond\n8. Var\n9. Math\n10. If\n11. Goto\n12. Exit\n13. request\n14. tags\n15. Administrator access\n16. Randomness\n17 discord.channel\n18.discord.member\n19. Sources\n\nUpdated last on 25/6/2023",
                'SlashScript is a small programming "language", or a script as I prefer to call it. The language isnt too big as its not meant to be used for bigger projects, but you can make quite a bit of fun stuff with it.',
                "Uploading a program is quite easy, you can either use ./upload_program or ./run_file. Using ./upload_program will save the program to ./program, whie ./run_file won't. Make sure to attach a .txt file with the script in it when uploading programs!",
                "Due to the whole language running on a single server, the limitations are quite high. The Maximum runtime of scripts is 120s (to stop infinite loops and memory hogging). For most basic scripts, this should be fine.",
                "SlashScript uses a lot of spaces ~~~for smart interactions with users~~ because the developer is too lazy to code proper compiling. Because of this, parenthesis and quotes aren't seen too often.",
                "SlashScript has a total of 10 commands, these are: Respond, Var, Math, If, Goto, Exit, random, discord.channel, discord.member and request. Each of these commands has a documentation page, feel free to check them.",
                "Respond is the equivalent of Print in python, the syntax is 'respond [message]', the message will appear at the end of execution. If you want to 'print' a variable, you need to use 'respond VAR [variable]', caps is necessary.",
                "Var works for assigning variables. SlashScript has 3 variable types: int/float, str and bool. The syntax is: 'var [name] [value]'. The type is calculated automatically.",
                "The math command can do math and turn it into a variable, usage is: 'math [storing-variable] [value1] [operator] [value2]'. The operator can be: +, -, *, /, %",
                "If is for conditionals. The syntax is: 'if [variable] [operator] [variable] [goto] <elsegoto>'. Goto means the line to go to if the condition is true. Elsegoto means the line to go to if the condition is false, and is optional. The operators are *exactly* like python's.",
                "Goto is for jumping lines, the syntax is 'goto [line]'",
                "Exit is as simple as it gets, it exits the program. The syntax is 'exit'",
                "Request is used to get http requests from the internet. This might be a bit complicated. Syntax: request [method] [url] <decoding> (At the time of writing, it might be a bit broken).",
                'Tags are small "commands" that allow you to tell the compiler things. These can be from accepting arguments to asking for administrator access. You can find the exact tags from the documentation',
                "Some actions (related to discord) may require administrator access from the runner, if you use these commands. You need to add the tag './ requiresadmin' at the start of the file (or anywhere before you use the commands), otherwise it will raise an error.",
                "You can generate a random number with the command 'random [storing-variable] [minimum] [maximum]. If the minimum value is bigger than the maximum, it will raise an error.'",
                "(BETA, expect issues) With the discord.channel command you can create channels (more features in the future), the syntax is 'discord.channel create [text/voice] [name]'.",
                "(BETA, expect issues) discord.member allows you to ban and kick members (more features in the future), the syntax is 'discord.member [ban/kick] [name] <reason>'.",
                "You can find both the bot's and the compiler's source code here: https://github.com/NotaKennen/dotSlashBot. You can DM the developer (memarios_) with extra questions or ideas."]
    pages = 19
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
        if ctx.message.attachments == []:
            await ctx.send("You didn't attach the program file, you can't upload an empty program.")
            return
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
    await ctx.send(f"The program has been saved! You can use it via ./program {name}")
    
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
async def program(ctx, name: str=None, *, arguments: str=None):
    # Only ./program
    if name is None:
        if not os.path.exists(f"Saved programs/{ctx.author.id}"):
            await ctx.send("You don't have any programs")
            return
        programstring = ""
        programlist = os.listdir(f'Saved programs/{ctx.author.id}')
        for i in programlist:
            programstring += f"- {i}" + "\n"
        await ctx.send(f"You have saved the following programs:\n\n{programstring}\nYou can these programs with ./program <program name>")

    # ./program <program name>
    else:
        if os.path.exists(f"Saved programs/{ctx.author.id}/{name}"):
            response = runprogram(ctx, name, ctx.author.id, "permanent", arguments)
            await ctx.send(response[1])
            return
        else:
            await ctx.send("The program does not exist")
            return
            
@bot.command(brief="Run a program without saving it")
async def run_file(ctx, *, arguments: str=None):
    # Get file from user
    try:
        if ctx.message.attachments == []:
            await ctx.send("You didn't attach the program file, you can't run an empty program.")
            return
        for attachment in ctx.message.attachments:
            await attachment.save(attachment.filename)
            filename = attachment.filename
            if not os.path.exists(f"temp programs/{ctx.author.id}"):
                os.makedirs(f"temp programs/{ctx.author.id}")
            shutil.move(filename, f"temp programs/{ctx.author.id}/{filename}")
    except Exception as e:
        await ctx.send(f"The bot had an issue running the program, most likely you forgot to attach the file:\n {e}")
        return

    try:
        response = runprogram(ctx, filename, ctx.author.id, "temp", arguments)
        await ctx.send(response[1]) # Send response
        os.remove(f"temp programs/{ctx.author.id}/{filename}") # Remove file
    except Exception as e:
        await ctx.send(response[1])

@bot.command(brief="Make custom commands for this server using SlashScript")
@commands.has_permissions(administrator=True)
async def custom_command_create(ctx, name=None, mode: str=None):
    if name is None:
        await ctx.send("You need to give the command a name!\nUsage: ./custom_command_create [name] [mode]")
        return
    elif mode is None:
        await ctx.send("You need to specify a mode for the command!\nAvailable modes: e (everyone), a (admins)\nUsage: ./custom_command_create [name] [mode]")
        return
    elif mode.lower() != "e" and mode.lower() != "everyone" and mode.lower() != "a" and mode.lower() != "admins":
        await ctx.send(f"Mode '{mode}' is not a valid mode. The modes are: e (everyone), a (admins)")
        return
    
    try:
        for attachment in ctx.message.attachments:
            # Save the file
            await attachment.save(attachment.filename)
        filename = attachment.filename

        # Check for missing paths
        if not os.path.exists(f"Server commands/{ctx.guild.id}/public"):
            os.makedirs(f"Server commands/{ctx.guild.id}/public")
        if not os.path.exists(f"Server commands/{ctx.guild.id}/private"):
            os.makedirs(f"Server commands/{ctx.guild.id}/private")

        # string
        if mode == "e" or mode == "everyone":
            mode = "public"
        elif mode == "a" or mode == "admins":
            mode = "private"

        # Rename it to match the name
        os.rename(filename, f"{name}.txt")

        # Move the file to the proper place
        shutil.move(f"{name}.txt", f"Server commands/{ctx.guild.id}/{mode}/{name}.txt")
    except Exception as e:
        await ctx.send(f"The bot had an issue saving the program: \n{e}")
        return
    
    await ctx.send(f"The command has been saved as {name}, you can use the command with ./cc {name}")

@bot.command(brief="Delete a custom command")
@commands.has_permissions(administrator=True)
async def custom_command_delete(ctx, name=None):
    if name is None:
        await ctx.send("You need to provide a name to delete the program!\nUsage: ./custom_command_delete [name]")
        return
    
    programs = []
    private_programs = []

    for file in os.listdir(f"Server commands/{ctx.guild.id}/public"):
        programs.append(file)
    for file in os.listdir(f"Server commands/{ctx.guild.id}/private"):
        private_programs.append(file)

    if f"{name}.txt" not in programs and f"{name}.txt" not in private_programs:
        await ctx.send("A custom command with that name doesn't exist!")
        return
    
    if f"{name}.txt" in programs:
        os.remove(f"Server commands/{ctx.guild.id}/public/{name}.txt")
        await ctx.send("The custom command has been deleted")
    elif f"{name}.txt" in private_programs:
        os.remove(f"Server commands/{ctx.guild.id}/private/{name}.txt")
        await ctx.send("The custom command has been deleted")
    else:
        await ctx.send("Something went horribly wrong")

@bot.command(brief="Run any of the server's custom commands")
async def cc(ctx, name: str=None, *, arguments: str=None):
    # Now we know if admin
    if ctx.message.author.guild_permissions.administrator:
        admin = True
    else:
        admin = False

    # Makes sure the path exists
    if not os.path.exists(f"Server commands/{ctx.guild.id}/public"):
        os.makedirs(f"Server commands/{ctx.guild.id}/public")
    if not os.path.exists(f"Server commands/{ctx.guild.id}/private"):
        os.makedirs(f"Server commands/{ctx.guild.id}/private")

    # If name is not input
    if name is None:
        programs = []

        try: # Get all the program files
            for file in os.listdir(f"Server commands/{ctx.guild.id}/public"):
                programs.append(file)
            if admin is True:
                for file in os.listdir(f"Server commands/{ctx.guild.id}/private"):
                    programs.append(file)
        except Exception as e:
            await ctx.send(f"Something went wrong! Most likely you don't have any custom commands:\n{e}")
            return
        
        # remove .txt from the name and make it the programs list
        templist = []
        for i in programs:
            templist.append(os.path.splitext(i))
        programs = []
        for i in templist:
            programs.append(i[0])

        # String fancycating
        strresponse = "" # Make a string
        for i in programs: # No lists
            strresponse += f"- {i}" # Add item to string
            strresponse += "\n" # Padding

        if strresponse == "":
            await ctx.send("You don't have any custom commands on this server")
            return

        await ctx.send(f"You have the following custom commands on your server:\n{strresponse}")

    if name is not None:
        programs = []
        private_programs = []

        for file in os.listdir(f"Server commands/{ctx.guild.id}/public"):
            programs.append(file)
        if admin is True:
            for file in os.listdir(f"Server commands/{ctx.guild.id}/private"):
                private_programs.append(file)

        if f"{name}.txt" not in programs and f"{name}.txt" not in private_programs:
            await ctx.send("A custom command with that name doesn't exist!")
            return
        
        if f"{name}.txt" in programs:
            # For some weird reason I decided that the author should be the private/public argument
            response = runprogram(ctx, name, "public", "custom", arguments)
            await ctx.send(response[1])
        elif f"{name}.txt" in private_programs:
            # see note above
            response = runprogram(ctx, name, "public", "custom", arguments)
            await ctx.send(response[1])
        else:
            await ctx.send("Something went horribly wrong")

@bot.command(brief="Send feedback!")
async def feedback(ctx, *, text: str=None):
    if text is None:
        await ctx.send("You have to enter feedback to send to me!\nUsage: ./feedback [text]")
        return
    channel = bot.get_channel(1048203207932919849)
    await channel.send(f"New feedback from {ctx.author}!\n\n{text}")

####################################################

with open("token.txt" , 'r') as f:
    token = f.read()

bot.run(token)