import re 
from time import time

def tokenize(code):
    """Makes the code into nice little lists that the compiler can handle"""
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
    def reg_split(input_string):
        """Split with regex from ';', but not when inside double quotes"""
        # Define a regular expression pattern to match the desired delimiter (;)
        # but not inside double quotes
        pattern = re.compile(r';(?=(?:[^"]*"[^"]*")*[^"]*$)')

        # Use re.split to split the string based on the pattern
        result = re.split(pattern, input_string)

        return result
    
    codeList = []
    code = code.replace("\n", "")
    cList = reg_split(code)
    for i in cList:
        filter = splitBySpace(i)
        if filter == ['']:
            continue
        codeList.append(filter)
    return codeList # FIXME: (2.1.0) make it so that comments are split properly (not working rn, you'd need to add a ; to the end of the comment)

def raiseError(error: str="Unknown error in compiler phase!"):
    """Simply "raises" an error"""
    return [f"({linenum}): {error}"]

def addToMemory(memory: dict, name: str, value):
    """Adds a value to a memory. Made to be a function in case I need to edit this later (without changing everything in the code)"""
    memory[name] = value
    return memory

def getMemory(memory: dict, name: str, error: str="Could not find value from memory"):
    """Gets a value from memory. Made to be a function for simpler error handling"""
    try:
        value = memory[name]
    except:
        return raiseError(error)
    return value #type: ignore (raiseError will take care of it)

def typeCheck(variable, supposedType: str=None): #type: ignore
    """Automatically converts the type to the correct type.
    supposedType can be set to force it to be one type. It'll raise an error if the type is not valid"""
    # No type input, guess the type
    variable = str(variable)
    if supposedType is None:
        if variable.isnumeric():
            return int(variable)
        elif variable == "True":
            return True
        elif variable == "False":
            return False
        else:
            return str(variable)
    else: # Force type to be the one input (or get error!)
        try:
            if supposedType == "str":
                return str(variable)
            elif supposedType == "int":
                return int(variable)
            elif supposedType == "bool":
                return bool(variable)
            else:
                return raiseError(f"No such type as {supposedType}.")
        except ValueError as e:
            raiseError(f"Expected value to be {supposedType}")

def evaluate(op1, operator, op2):
    """Basically an if statement but it returns you the output"""
    def equals(op1, op2):
        return op1 == op2

    def not_equals(op1, op2):
        return op1 != op2

    def greater_than(op1, op2):
        return op1 > op2

    def greater_than_or_equal(op1, op2):
        return op1 >= op2

    def less_than(op1, op2):
        return op1 < op2

    def less_than_or_equal(op1, op2):
        return op1 <= op2

    comparison_functions = {
        "==": equals,
        "!=": not_equals,
        ">": greater_than,
        ">=": greater_than_or_equal,
        "<": less_than,
        "<=": less_than_or_equal,
    }

    if operator in comparison_functions:
        return comparison_functions[operator](op1, op2)
    else:
        return raiseError(f"Invalid operator")
            
def arithmetic(op1, operator, op2):
    """Runs an arithmetic operation, and returns you the output"""
    def add(op1, op2):
        return op1 + op2

    def subtract(op1, op2):
        return op1 - op2

    def multiply(op1, op2):
        return op1 * op2

    def divide(op1, op2):
        if op2 != 0:
            return op1 / op2
        else:
            raiseError("Division by zero")

    def power(op1, op2):
        return op1 ** op2

    arithmetic_functions = {
        "+": add,
        "-": subtract,
        "*": multiply,
        "/": divide,
        "^": power,
    }

    if operator in arithmetic_functions:
        return arithmetic_functions[operator](op1, op2)
    else:
        raiseError(f"Invalid arithmetic operator")

def checkForVariable(variableMemory, value):
    """Checks if a string is referring to a variable"""
    if value[0] == "&": # if the first letter of the value is &, get the variable that it mentions
        value = getMemory(variableMemory, value[1:], f"No such variable as {value[1:]}")
    return value

#! - - - - - (compiler starts here)

def compile(code, admin: bool, arguments: list):
    startingTime = time()
    global linenum

    code = tokenize(code)
    response = [] # The response that we're giving back
    functionMemory = {} # Memory which stores Functions / functionMemory format is { "function-name": line-number }
    variableMemory = {} # ^ but with variables / variableMemory format is { "variable-name": value }
    skipLine = 0 # The line we need to skip to (Should never be < 0, 0 means that we aren't skipping lines)
    returnLine = 0 # Storage for when we need to return to the line we started on (in functions)
    inFunction = False # Whether we are in a function or not
    functionCalled = False # Whether we are in a function THAT HAS BEEN CALLED or not
    conditionalDepth = 0 # Whether we are in a conditional statement or not (Should never be < 0)
    skipTill = "" # Change this to skip until you hit a command that you need
    while True:
        linenum = 0
        for command in code: 
            linenum += 1

            # Time limit
            if time() - startingTime > 300: return raiseError("The program took too long to run, so it was terminated")

            # Logic for line skipping
            # SkipTill = "" / skip until it hits this string, only counts command[0], does not go backwards like SkipLine
            # SkipLine = """ / line number you want to skip to (also goes backwards if you need)
            if skipTill != "":
                if command[0] == skipTill:
                    skipTill = ""
                else:
                    continue
            if skipLine != 0:
                if linenum < skipLine:
                    continue # We skip this line
                elif linenum == skipLine:
                    skipLine = 0 # we stop skipping lines
                else:
                    break # we need to break from the loop to get back to the start

            """#? Command register
            if command[0] is a "registered" command (as in declared here) you can make it run stuff. Any arguments will be command[(number)]
            The "registering" will be as simple as running an if command[0] is the name of the command, as you can see below
            """

            if command == []: # Empty command (newline)
                continue

            elif command[0] == "respond":
                value = command[1]
                value = checkForVariable(variableMemory, value)
                if command[2] == "nonstack":
                    response[-1] += value
                    continue
                response.append(value)

            elif command[0] == "var":
                value = command[3]

                # Variable checking
                value = checkForVariable(variableMemory, value)
                
                # Type checking
                value = typeCheck(value, command[1])
                
                addToMemory(variableMemory, command[2], value)

            elif command[0] == "./":
                # Tags
                if command[1] == "argument":
                    name = command[2]
                    value = int(typeCheck(command[3], "int")) #type: ignore
                    try:
                        value = arguments[value-1]
                    except IndexError:
                        return raiseError(f"Not enough arguments provided")
                    except Exception as e:
                        return raiseError(f"Unknown error: {e}")
                    value = typeCheck(value)
                    value = addToMemory(variableMemory, name, value)

                elif command[1] == "noadmin":
                    admin = True

                elif command[1] == "admin":
                    if admin is False:
                        raiseError("Admin privilige is required to run this command")
                
                else:
                    return raiseError(f"No tag called {command[1]}")

            elif command[0] == ":f":
                #! # FIXME: (2.1.0) Function in function raises error!
                addToMemory(functionMemory, command[1], linenum)
                inFunction = True
                skipTill = "end"

            elif command[0] == "endfunc":
                if not inFunction and not functionCalled:
                    return raiseError(f"Not in a function!")
                if functionCalled:
                    skipLine = returnLine
                    returnLine = 0
                inFunction = False

            elif command[0] == "function":
                funcLine = int(getMemory(functionMemory, command[1], f"Function not found!")) #type: ignore
                skipLine = funcLine + 1
                returnLine = linenum + 1
                functionCalled = True
                inFunction = True

            elif command[0] == "jump":
                skipLine = int(command[1])
            
            elif command[0] == "if":
                # Get the arguments for op1, op2 and the operator 
                op1 = command[1]
                op2 = command[3]
                operator = command[2]

                # Check for variables
                op1 = checkForVariable(variableMemory, op1)
                op2 = checkForVariable(variableMemory, op2)

                op1 = typeCheck(op1)
                op2 = typeCheck(op2)

                value = evaluate(op1, operator, op2)
                if value is False:
                    skipTill = "endif"
                conditionalDepth += 1
                
            elif command[0] == "endif":
                if conditionalDepth <= 0:
                    return raiseError(f"Not in a conditional statement!")
                conditionalDepth = -1
                continue

            elif command[0] == "math":
                storage = command[1]
                op1 = command[2]
                op2 = command[4]
                operator = command[3]

                op1 = typeCheck(checkForVariable(variableMemory, op1), "int")
                op2 = typeCheck(checkForVariable(variableMemory, op2), "int")

                value = arithmetic(op1, operator, op2)
                
                addToMemory(variableMemory, storage, value)

            else: # Command does not exist
                return raiseError(f"No such command as {command[0]}")

        # End of while loop
        if skipLine == 0:
            return response