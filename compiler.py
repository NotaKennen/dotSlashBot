from queue import Queue
import requests # exec() doesn't see it as a needed import, even though it is (?)
from random import randint # Same thing as ^
import time

def compile(commandlist, responsequeue, actionqueue, admin_access: bool=False, arguments: list=None):

    # Fancier exceptions because the older ones sucked
    def raiseError(error: str):
        with responsequeue.mutex:
            responsequeue.queue.clear()
        with actionqueue.mutex:
            actionqueue.queue.clear()
        responsequeue.put(["ERROR LOG", error])
        actionqueue.put(["ERROR LOG", error])
        exit()

    def checkTimeout(starttime):
        X = 120
        if time.time() > starttime + X:
            raiseError("The script was taking too long, so it was terminated.")

    def addAction(action: str):
        actionlist.append(action)

    commands = []
    for i in commandlist:
        i = i.replace("\n", "")
        commands.append(i)

    # Non-resetting obvious variables
    gotoline = None
    response = []
    actionlist = []
    requiresadmin = False
    starttime = time.time()
    argumentnumber = 0

    # Compiler loop
    while True:
        # Obvious variables
        linenum = 0
        skipline = False

        # Command runner
        for line in commands:
            checkTimeout(starttime)

            # linenum + and command split 
            linenum += 1
            command = line.split(" ")

            ### LOGIC ###
 
            # Admin logic
            if requiresadmin == True and admin_access == False:
                raiseError("You don't have the required administrative access to run this program.")

            # Gotoline logic
            if gotoline is not None:
                if gotoline > linenum:
                    skipline = True
                elif gotoline == linenum:
                    skipline = False
                    gotoline = None
                elif gotoline < linenum:
                    break
            if skipline is True:
                continue

            ### COMMANDS ###

            # Empty line
            if command == ['']:
                continue

            # Comment
            elif command[0] == "#" or command[0] == "//":
                continue

            # tags
            elif command[0] == "./":
                if command[1] == "requiresadmin":
                    requiresadmin = True
                elif command[1] == "addargument":
                    argumentvariable = command[2]
                    exec(f"{argumentvariable} = '{arguments[argumentnumber]}'")
                    argumentnumber += 1
                else:
                    raiseError(f"({linenum}) Invalid tag: ({command[1]})")

            # Respond
            elif command[0] == "respond":

                if command[1] == "VAR": # User prints variable
                    try:
                        exec(f"response.append({command[2]})")
                        continue
                    except Exception as e:
                        raiseError(f"({linenum}) Unknown error: {e}")
                
                command = line.split(" ", 1)
                response.append(command[1])
                continue

            # Variable handling
            elif command[0] == "var":
                varname = command[1]
                varvalue = command[2]

                if varvalue == "True" or varvalue == "False": # Value is bool
                    if varvalue == "True":
                        varvalue = True
                    else:
                        varvalue = False

                elif varvalue.isnumeric(): # Value is int
                    varvalue = int(varvalue)

                else: # Value is string
                    varvalue = str(line.split(" ", 2)[2])
                    exec(f'{varname} = str("{varvalue}")')
                    continue

                exec(f"{varname} = {varvalue}")
                continue

            # Simple math 
            elif command[0] == "math":
                try:
                    storage = command[1]
                    value1 = command[2]
                    operator = command[3]
                    value2 = command[4]

                    # Variable acceptance
                    try:
                        if not value1.isnumeric():
                            exec(f"value1 = int({value1})")
                        if not value2.isnumeric():
                            exec(f"value2 = int({value2})")
                    except:
                        raiseError(f"({linenum}) Value 1 or value 2 is not an integer, or the variable does not include an integer.")

                    exec(f"{storage} = {value1} {operator} {value2}")
                except IndexError:
                    raiseError(f"({linenum}) Math command is missing arguments")
                except ArithmeticError:
                    raiseError(f"({linenum}) Math command is invalid")
                except Exception as e:
                    raiseError(f"({linenum}) Unknown error: {e}")

            # Conditional stuff
            elif command[0] == "if":
                try:
                    # Get operators and other variables
                    op1 = command[1]
                    condition = command[2]
                    op2 = command[3]
                    goto = command[4]
                    try: # Else goto line number
                        elsenum = command[5]
                    except IndexError:
                        elsenum = None

                    # if op1 or op2 are variables: if (variable)
                    if not op1.isnumeric():
                        exec(f"op1 = {command[1]}")
                    else:
                        op1 = int(op1)
                    if not op2.isnumeric():
                        exec(f"op2 = {command[3]}")
                    else:
                        op2 = int(op2)

                    # if goto or else are variables
                    if not goto.isnumeric():
                        exec(f"goto = {command[1]}")
                    else:
                        goto = int(goto)
                    if not elsenum.isnumeric():
                        exec(f"elsenum = {command[3]}")
                    else:
                        elsenum = int(elsenum)
                
                except IndexError:
                    raiseError(f"({linenum}) If command is missing arguments")
                except Exception as e:
                    raiseError(f"({linenum}) Unknown error: {e}")

                gotoIf = None
                if elsenum is not None:
                    exec(f'if {op1} {condition} {op2}: gotoIf = "if"')
                    if gotoIf is None:
                        gotoIf = "else"
                else:
                    exec(f"if {op1} {condition} {op2}: gotoIf = 'if'")

                # If not int
                try:
                    goto = int(goto)
                    elsenum = int(elsenum)
                except ValueError:
                    raiseError(f"({linenum}) Expected goto number to be integer")

                if gotoIf == "if": # Resulted into the IF (TRUE)
                    gotoline = goto
                elif gotoIf == "else": # Resulted into the ELSE (FALSE)
                    gotoline = elsenum
                else: # FALSE But no else
                    continue
                break # Go to line break
                # Go to line

            # Goto line
            elif command[0] == "goto":
                if command[1].isnumeric():
                    gotoline = int(command[1])
                    break
                else:
                    raiseError(f"({linenum}) Expected goto argument to be integer")

            # Functions # TODO
            elif command[0] == "func":
                funcname = command[1]

            # Exit
            elif command[0] == "exit":
                gotoline = None
                break

            # Http request
            elif command[0] == "request":
                try:
                    variable = command[1]
                    rtype = command[2]
                    address = command[3]
                    posttype = None
                    try:
                        posttype = command[4]
                    except IndexError:
                        posttype = None

                    exec(f"{variable} = requests.{rtype}('{address}')")
                    if posttype is not None:
                        if posttype == "json":
                            posttype = "json()"
                        elif posttype == "text": # I know this here sucks
                            posttype = "text"
                        elif posttype == "content":
                            posttype = "content"
                        else:
                            raiseError(f"({linenum}) Unknown posttype")
                            
                        exec(f"{variable} = {variable}.{posttype}") #FIXME: idk why is it only giving out JsonDecodeError, most likely improper testing?
                except Exception as e: 
                    raiseError(f"({linenum}) This error is here to prevent crashes, you did something wrong: {e}")

            # RNG
            elif command[0] == "random":
                storage = command[1]
                minimum = command[2]
                maximum = command[3]
                if minimum > maximum:
                    raiseError(f"({linenum}) Minimum value is higher than maximum value.")
                exec(f"{storage} = random.randint({minimum}, {maximum})")

            # channels
            elif command[0] == "discord.channel":
                if requiresadmin is False:
                    raiseError("You don't have the required administrative access to run this program (or you forgot to add the ./requiresadmin tag)!")
                # Create text channels
                if command[1] == "create":
                    if command[2] == "text":
                        addAction(f"await guild.create_text_channel('{command[3]}')")
                    elif command[2] == "voice":
                        addAction(f"await guild.create_voice_channel('{command[3]}')")
                    else:
                        raiseError(f"({linenum}) Invalid argument (discord.channel create {command[3]}. (Expected channel type (text/voice))")
                
                # TODO: allow users to delete channels, but find a proper way to do it without them abusing it
                # most likely use names, error handling hell awaits.

                else: # Invalid arguments on c[1]
                    raiseError(f"({linenum}) Invalid argument (discord.channel {command[1]}) (expected channel action)")

            # Raise an error on unknown commands
            else:
                raiseError(f'({linenum}) Invalid command, "{line}"')
            
        if gotoline is None:
            break

    # Response output
    if actionlist == []:
        actionlist = None
    actionqueue.put(actionlist)
    if response == []:
        response = "(No response) The program ran succesfully"
    responsequeue.put(response)