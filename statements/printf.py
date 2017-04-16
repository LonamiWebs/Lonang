from .statement import Statement
from variables import Variable
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


def printf(c, m):
    """Prints a string with optional formatted values. For instance:
        printf "I'm %d years old, you %d" % ax, bx
        printf stringVariable
    """
    # TODO Add support for not inlining
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
    c.add_code('push ax',
               'push dx',
               'mov ah, 9')

    string = m.group(1).strip()
    args_at = string.rfind('%')
    if args_at == -1:
        args = None
    else:
        args = [a.strip() for a in string[args_at+1:].split(',')]
        string = string[:args_at].strip()

    # Now, we have the right string and the arguments used
    if args:
        # 1. Find %X's
        substrings = re.split(r'%[sd]', string)
        arg_types = re.findall(r'%[sd]', string)
        if '%d' in arg_types:
            raise ValueError('Formatting %d is not yet supported')

        # 2. Print: substring, formatted, substring, formatted, etc.
        for i in range(len(substrings)):
            if i > 0:
                # Format the previous string (there must be n-1 args),
                # which for now has to be a string (TODO Support integers)
                var = c.variables[args[i-1]]
                c.add_code(f'lea dx, {var.name}')
                c.add_code(f'int 21h')

            if substrings[i]:
                define_and_print(c, substrings[i])
    else:
        if string in c.variables:
            variable = c.variables[string]
            if variable.type == 'string':
                c.add_code(f'lea dx, {variable.name}')
                c.add_code(f'int 21h')
            else:
                # TODO Convert int to string, then parse show it
                raise ValueError('Printing numbers is not yet supported')

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
