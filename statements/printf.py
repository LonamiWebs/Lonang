from .statement import Statement
from variables import Variable
from utils import helperassign
from builtin_functions import define_integer_to_string
import re


def define_and_print(c, string):
    """Defines a new variable with an unique name
        for 'string', and prints it to the screen
    """
    if string:
        var = Variable(c.get_uid(), 'string', string)
        if var.value != "'$'":
            c.add_variable(var)
            c.add_code(f'lea dx, {var.name}')
            c.add_code(f'int 21h')


def load_integer(c, var_name):
    """Converts the given integer variable into a string
        and loads it to dx, so it's ready to be printed
    """
    itos = define_integer_to_string(c)
    helperassign(c, itos.params[0], var_name)
    c.add_code(f'call {itos.name}')
    # AX was lost, we need to set the right value again TODO Improve ITOS!!
    c.add_code(f'mov ah, 9')
    c.add_code(f'lea dx, {itos.returns}')


def printf(c, m):
    """Prints a string with optional formatted values. For instance:
        printf "I'm %d years old, you %d" % ax, bx
        printf stringVariable
    """
    # TODO Possibly add support for not inlining
    #      Inlining really shines when there are actually formatted values:
    #
    #      If inlining:
    #           5 instructions; push/pop ax/dx, mov ah 9
    #        + 2n (where n is the number of strings, lea + int)
    #
    #      If not inlining (the first 7 are only written once, ran many times):
    #          7n instructions; function definition, push/pop ax, mov ah 9, int
    #        +  2 instructions; push/pop dx
    #        + 2n (where n is the number of strings, lea + int)
    #
    # Determine the string (or variable) to print and its arguments
    string = m.group(1).strip()
    args_at = string.rfind('%')
    if args_at == -1:
        args = None
    else:
        args = [a.strip() for a in string[args_at+1:].split(',')]
        string = string[:args_at].strip()

    # Once, so we can restore it at the very end
    c.add_code('push ax',
               'push dx')

    # Since 'ax' and 'dx' are needed for printing, we might
    # need to push them more times to pop them as required.
    # Also in reversed order, since the stack pops on reverse
    for a in reversed(args):
        if a in ['ax', 'dx']:
            c.add_code(f'push {a}')

    # After we saved the values we may later need, set up the print function
    c.add_code('mov ah, 9')

    # Now, we have the right string and the arguments used
    if args:
        # 1. Find %X's
        substrings = re.split(r'%[sd]', string)
        arg_types = re.findall(r'%[sd]', string)

        # 2. Print: substring, formatted, substring, formatted, etc.
        for i in range(len(substrings)):
            if i > 0:
                # Format the arguments, skipping 1 normal string (thus -1)
                var_name = args[i-1]
                arg_type = arg_types[i-1]

                # Load the argument into 'dx' depending on its type
                #
                # This assumes that the user entered the right type
                # TODO Don't assume that the user entered the right type
                if arg_type == '%s':
                    c.add_code(f'lea dx, {var_name}')
                elif arg_type == '%d':
                    if var_name in ['ax', 'dx']:
                        # Special, this was pushed previously
                        c.add_code('pop ax')
                        load_integer(c, 'ax')
                        c.add_code('mov ah, 9')
                    else:
                        load_integer(c, var_name)
                else:
                    raise ValueError(f'Regex should not have allowed {arg_type}')

                # Call the interruption to print the argument
                c.add_code(f'int 21h')

            # Argument formatted, print the next part of the string
            define_and_print(c, substrings[i])

    # No arguments, only a variable or a raw string
    else:
        if string in c.variables:
            # Using a variable, load and call the interruption
            variable = c.variables[string]

            if variable.type == 'string':
                c.add_code(f'lea dx, {variable.name}')
            else:
                load_integer(c, var.name)

            c.add_code(f'int 21h')
        else:
            # Assume inmediate value, convert it to string if required
            # TODO This won't check a string variable starts and ends with "!
            if string[0] != '"':
                string = f'"{string}"'

            define_and_print(c, string)

    c.add_code('pop dx',
               'pop ax')

printf_statement = Statement(
    r'printf  (.+)',
    printf
)
