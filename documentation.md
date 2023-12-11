# Basic usage (discord)
You can upload a command to the server with './upload_cc [name]', then just attach the program file to the message. You can run a set command with './cc (name)'. You can delete one of your server's commands with './delete_cc (name)'. To see all your server's commands, run './custom_commands'.

# Syntax
The syntax is be assembly-like and it should be pretty easy to understand. The language is based on commands that you can call to make stuff happen. All commands end with ';' (semicolon). Any code can be split into multiple lines, the command will end when a semicolon appears. Any spaces that are not strings (not inside double quotes (")) are treated as an end to the current argument, and any non-stringed text will be treated as "plain text" which you can still use as an argument, but you can't use spaces. You can comment text by using the '#' symbol on the commented line, just like in python.

# Commands
### Respond
Prints a response to the output, the output will be displayed in the channel the command was executed when the program is done. You can only do one response at a time, they cannot be stacked like in python (print("Text", variable, "more-text") < not like this!). If you want to have a variable on a single line, you can use "stacking" responses by adding 'stack' at the end of the response, this will simply add it to the previous response. Using stack will not add anything to the old string, so remember to place a space before your new response. 
Usage: 
"respond (value);"
"respond &variable;"
"respond "insert text here!;""
"respond "text here" stack;"


### Variables
You can assign a variable using 'var'. In SS you can use Strings, Integers and Booleans. Lists, Tables, Chars etc do not exist as of 2.0.0. If you want to use a variable as an argument in a command, you can do that with '&variable'.
Usage: 
"var (type) (variable-name) (assigned value);"
"var int variable 10;"


### Conditionals
You can run a conditional operation using 'if'. Operators are the same that Python uses. After you're done with the conditional code, you need to end the code with 'endif;'. If you want to continue with an 'else' statement, you must put it after 'endif'. You need to end the 'else' with an 'endif'.
Usage:
"if (variable/value) (operator) (variable/value);"
"if &value1 == &value2;"
"endif;"
"else;"


### Functions
You can declare a function using ':f' and call a function with 'function'. To end the declaration of a function, you need to use ':endf'. Functions will only be put into "function memory" if the compiler has actually went through them. In practice, you just have to declare your functions on any line above the code before you use it. As of 2.0.0, you cannot make arguments for functions, though that is planned in the future.
Usage:
":f (function-name); (code); endf;"
"function (function-name);"

### Math
You can do arithmetic operations with the 'math' command. The return will be stored in a variable, you can overwrite one of the used variables if you want to.
Usage:
"math (storage-variable) (value) (operator) (value);"
"math result 10 + 10;" (places the value 20 inside the variable 'result')
"math result &result + 10;" (adds 10 to the variable 'result')

### Tags
Tags are simple "commands" that you can call to edit the response or mechanics of the code. Just like functions, tag will only apply if they have been ran. So for example if you skip over a tag, it won't do anything. If you wan't to apply tags everywhere in the code, it is suggested to place them at the top of the code, if you want to use tags conditionally, you can do that with a simple conditional statement.
Currently there are 3 tags *'admin', 'noadmin' and 'argument'*. Admin makes it so that the command is only executable by people who have the administrator permission on discord, by default, any command that changes the discord server (creating new channels, changing roles etc) will require administrator anyway, unless you use the noadmin tag. Noadmin will make it so, that no matter what, the program will not require any kinds of administrative permissions, this tag is **extremely dangerous**. Argument gets the argument matching to the argument number (for example the in the command "./cc ProgramName.txt argument1 argument2", "./ argument storage 1" would get the first argument), arguments will then be stored in the assigned variable.
Usage:
"./ admin"
"./ noadmin"
"./ argument (storage-variable) (argument-number)"

# Code
The actual code in the compiler is split into 2 parts. Compiler.py has the compiler itself, while bot.py has the bot interface and everything about the bot. The compiler will return the response in a list, with each response being one value in it. The bot will then send the response list values one at a time. 