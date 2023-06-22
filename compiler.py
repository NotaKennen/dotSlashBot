# Exceptions
class CommandError(Exception):
    pass
class UnknownException(Exception):
    pass
class VariableError(Exception):
    pass
# End

"""
    Commands:
     - Respond
     - 
"""

import discord
from discord.ext import commands
from queue import Queue
import requests

def compile(commandline, queue):

    commands = []
    for i in commandline:
        i = i.replace("\n", "")
        commands.append(i)

    # Non-resetting obvious variables
    gotoline = None
    response = []
    while True:

        # Obvious variables
        linenum = 0
        skipline = False

        # Command runner
        for line in commands:

            # linenum + and command split 
            linenum += 1
            command = line.split(" ")

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

            # Empty line
            if command == ['']:
                continue

            # Comment
            elif command[0] == "#" or command[0] == "//":
                continue

            # Respond
            elif command[0] == "respond":

                if command[1] == "VAR": # User prints variable
                    try:
                        exec(f"response.append({command[2]})")
                        continue
                    except Exception as e:
                        raise UnknownException(f"({linenum}) Unknown error: {e}")
                
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
                try: # TODO: allow variables
                    storage = command[1]
                    value1 = command[2]
                    operator = command[3]
                    value2 = command[4]

                    exec(f"{storage} = {value1} {operator} {value2}")
                except IndexError:
                    raise IndexError(f"({linenum}) Math command is missing arguments")
                except ArithmeticError:
                    raise ArithmeticError(f"({linenum}) Math command is invalid")
                except Exception as e:
                    raise UnknownException(f"({linenum}) Unknown error: {e}")

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
                    raise VariableError(f"({linenum}) If command is missing arguments")
                except Exception as e:
                    raise UnknownException(f"({linenum}) Unknown error: {e}")

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
                    raise VariableError(f"({linenum}) Expected goto number to be integer")

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
                    raise VariableError(f"({linenum}) Expected goto number to be integer")

            # Functions # TODO
            elif command[0] == "func":
                funcname = command[1]

            # Exit
            elif command[0] == "exit":
                gotoline = None
                break

            # Http request
            elif command[0] == "request":
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
                    elif posttype == "text":
                        posttype = "text"
                    elif posttype == "content":
                        posttype = "content"
                    else:
                        raise VariableError(f"({linenum}) Unknown posttype")
                        
                    exec(f"{variable} = {variable}.{posttype}")


            # Raise error on unknown commands
            else:
                raise CommandError(f'({linenum}) Invalid command, "{line}"')
        if gotoline is None:
            break
    queue.put(response)