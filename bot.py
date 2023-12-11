import discord
from discord.ext import commands
from compiler import compile #! Compiler
from multiprocessing.pool import ThreadPool
import time
import os

PROD = False # Production environment (bool)
VERSION = "2.0.1" # Bot version 1.(major).(minor) (String)
STARTTIME = time.time()

if PROD == True:
	from flask import Flask
	from threading import Thread

	app = Flask('') 

	@ app.route('/')
	def main():
		return "DotSlash is online"


	def run():
		app.run(host="0.0.0.0", port=8000)


	def keep_alive():
		server = Thread(target=run)
		server.start()

	keep_alive()

def runprogram(ctx, code, argumentsStr: str=""): #type: ignore
	"""
	Runs a program in the compiler. The only argument is the code and the message context (ctx)
	"""

	def splitBySpace(input_string):
		"""Splits the string by spaces, except for all the spaces inside double quotes"""
		result = []
		current_word = ""
		inside_quotes = False

		for char in input_string:
			if char == ' ' and not inside_quotes:
				if current_word:
					result.append(current_word)
					current_word = ""
			elif char == '"':
				inside_quotes = not inside_quotes
			else:
				current_word += char

		if current_word:
			result.append(current_word)

		return result
 
	arguments = splitBySpace(argumentsStr)

	admin = ctx.message.author.guild_permissions.administrator

	try: # Execution
		thread = ThreadPool(processes=1) # Fake thread I guess
		threadval = thread.apply_async(compile, args=(code, admin, arguments)) # make a "thread"
		result = threadval.get(timeout=1)

		if result is False:
			return (False, f"Error in code: {result[1]}")

		response = ""
		for i in result:
			response += "> " + i + "\n"

		return (True, response)
		
	except Exception as e: # Failure catching
		return (False, f"Unknown error: {e}")

async def get_attachments(ctx, path, name: str=None): #type: ignore
	if ctx.message.attachments:
		for attachment in ctx.message.attachments:
			# Make paths
			try:
				os.makedirs(path)
			except FileExistsError:
				pass
			except:
				return False

			# Download the file
			file_content = await attachment.read()

			if name is None:
				name = attachment.filename
			if not name[-4:] == ".txt":
				name += ".txt"

			# Save the file or process its content
			with open(f"{path}/{name}", 'wb') as f:
				f.write(file_content)
			return name
	else:
		return False

def startCrashLog():
	def keepUpdating():
		while True:
			time.sleep(5)
			with open("Bot storage/crashlog.txt", "w") as crashlog:
				crashlog.write(str(time.time()))
	try:
		with open("Bot storage/crashlog.txt", "r") as crashlog:
			crashtime = float(crashlog.read())
	except Exception:
		with open("Bot storage/crashlog.txt", "w") as crashlog:
			crashlog.write(str(time.time()))
		crashtime = 0

	thread = ThreadPool(processes=1) # Fake thread I guess
	thread.apply_async(keepUpdating, args=()) # make a "thread"

	return time.time() - crashtime

## Pre startup logic
CRASHTIME = round(startCrashLog(), 2)
units = "seconds"
if CRASHTIME > 120:
	CRASHTIME = round(CRASHTIME / 60, 2)
	units = "minutes"
if CRASHTIME > 60:
	CRASHTIME = round(CRASHTIME / 60, 1)
	units = "hours"
if CRASHTIME > 48:
	CRASHTIME = int(round(CRASHTIME / 24, 0))
	units = "days"
##

print("----------------------------------------------")

intents = discord.Intents.all()
if PROD is True:
	bot = commands.Bot(command_prefix='./',intents=intents)
else:
	bot = commands.Bot(command_prefix='b./',intents=intents)

@bot.event
async def on_ready():
	if PROD:
		botactivity = discord.Activity(type=discord.ActivityType.watching, name="you code [./]")
	else:
		botactivity = discord.Activity(type=discord.ActivityType.streaming, name="a beta version of DotSlash")

	await bot.change_presence(activity=botactivity, status=discord.Status.online)
	print('Logged in as')
	print(bot.user)
	print(f"Offline for {CRASHTIME} {units}")
	print('----------------------------------------------')

@bot.command(brief="Learn about SlashScript!")
async def documentation(ctx):
	await ctx.send("You can find documentation on the Github page:\nhttps://github.com/NotaKennen/dotSlashBot/blob/main/documentation.md")

@bot.command(brief="Upload a Custom Command")
@commands.has_permissions(administrator=True)
async def upload_cc(ctx, *, name: str=None): #type: ignore
	result = get_attachments(ctx, f"Bot storage/Server commands/{ctx.guild.id}", name)
	if not result:
		await ctx.send("No file attached!")
		return
	await ctx.send(f"Uploaded the command as {result}")

@bot.command(brief="Delete a Custom Command")
@commands.has_permissions(administrator=True)
async def delete_cc(ctx, *, name: str=None): #type: ignore
	try:
		path = f"Bot storage/Server commands/{ctx.guild.id}/{name}"
		# Check if the file exists
		if os.path.exists(path):
			# Delete the file
			os.remove(path)
			await ctx.send("The command has been deleted")
		else:
			await ctx.send(f"There isn't a command called {name}")
	except Exception as e:
		await ctx.send(f"Unknown error: {e}")

@bot.command(brief="Shows you the commands on this server")
async def custom_commands(ctx):
	try:
		path = f"Bot storage/Server commands/{ctx.guild.id}"
		# List all files in the directory
		files = os.listdir(path)

		# Filter out non-files (directories, etc.)
		files = [file for file in files if os.path.isfile(os.path.join(path, file))]

		response = "Custom command files on this server:\n"
		for i in files:
			response += "> " + i + "\n"
		await ctx.send(response)
	except FileNotFoundError:
		await ctx.send("This server does not have any commands")

@bot.command(brief="Run a custom command")
async def cc(ctx, name: str=None, *, arguments: str=""): #type: ignore
	if name is None:
		await ctx.send("You need to provide a name for the command\nUsage: ./cc (name)")
		return
	try:
		path = f"Bot storage/Server commands/{ctx.guild.id}/{name}"
		with open(path, 'r') as file:
			# Read and print the contents of the file
			code = file.read()
		response = runprogram(ctx, code, arguments)
		await ctx.send(response[1])
	
	except FileNotFoundError:
		await ctx.send(f"The command {name} does not exist.")
	except Exception as e:
		await ctx.send(f"Unknown error: {e}")

@bot.command(brief="Uptime statistics")
async def uptime(ctx):
	timer = time.time() - STARTTIME
	unit = "seconds"
	if timer > 120:
		timer = timer / 60
		unit = "minutes"
	if timer > 60:
		timer = timer / 60
		unit = "hours"
	await ctx.send(f"The bot has been up for {round(timer,1)} {unit}\nLast offline for {CRASHTIME} {units}\n\nBot latency: {round(bot.latency*1000)} ms\n\nRunning version {VERSION}")

####################################################

if not PROD:
	with open("untoken.txt" , 'r') as f:
		bot.run(f.read())
else:
	bot.run(os.getenv("discord-token")) # type: ignore