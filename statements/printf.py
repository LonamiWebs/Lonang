from .statement import Statement
from variables import Variable
from utils import helperassign
from builtin_functions import define_integer_to_string, define_tmp_variable
import re


def define_and_print(c, string):
    """Defines a new variable with an unique name
        for 'string', and prints it to the screen
    """
    if not string or not string.strip('"'):
        return

    # First try finding an existing string variable with the same content
    # that we wish, if it exists, don't waste memory creating yet another one
    enc = Variable.escape_string(string)
    var = next((v for v in c.variables.values() if v.value == enc), None)
    if not var:
        # No luck, create a new variable TODO This will escape the string again!
        var = Variable(c.get_uid(), 'string', string)
        c.add_variable(var)

    # Now we have an existing variable with the content we want to show
    c.add_code(f'lea dx, {var.name}')
    c.add_code(f'int 21h')


def load_integer(c, op):
    """Converts the given integer operand into a string
        and loads it to dx, so it's ready to be printed
    """
    itos = define_integer_to_string(c)
    helperassign(c, itos.params[0], op)
    c.add_code(f'call {itos.name}')
    # AX was lost, we need to set the right value again TODO Improve ITOS!!
    c.add_code(f'mov ah, 9')
    c.add_code(f'lea dx, {itos.returns}')


def is_ax_or_dx_variant(op):
    """Returns True if the register is 'ax', 'dx' or a variant"""
    return op[0] in 'ad' and op[-1] in 'xhl'


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
    # Retrieve the captured values
    string = m.group(1)
    args = c.get_operands(m.group(2))
    var = m.group(3)

    # Save the registers used for calling the print interruption
    c.add_code('push ax',
               'push dx')

    # string/args and var are mutually exclusive
    if var:
        op = Operand(c, var, assert_vector_access=False)
        if op.is_mem:
            # Using a variable, load and call the interruption
            if op.type == 'string':
                c.add_code(f'lea dx, {op}')
            else:
                load_integer(c, op.code)

            c.add_code(f'mov ah, 9')
            c.add_code(f'int 21h')

        elif op.is_reg:
            # Using a register, which means we need to load an integer
            load_integer(c, op)
            c.add_code(f'mov ah, 9')
            c.add_code(f'int 21h')

        else:
            # Assume inmediate integer value
            c.add_code(f'mov ah, 9')
            define_and_print(c, f'"{op.name}"')

    else:
        # Captured a string, with possibly formatted arguments
        #
        # Since 'ax' and 'dx' are needed for printing, we need to save them.
        # We could use the stack, however, we would need to push as many times
        # as we encountered one of the offending registers. Also, the stack
        # doesn't support the 8-bit versions of these registers, so we simply
        # use a temporary variable.
        for a in args:
            if is_ax_or_dx_variant(a):
                helperassign(c, define_tmp_variable(c, a), a)

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
                    op = args[i-1]
                    format_type = arg_types[i-1]

                    # Load the argument into 'dx' depending on its type
                    #
                    # This assumes that the user entered the right type
                    # TODO Don't assume that the user entered the right type
                    if format_type == '%s':
                        c.add_code(f'lea dx, {op}')
                    elif format_type == '%d':
                        if is_ax_or_dx_variant(op):
                            # Special, this was saved previously
                            load_integer(c, define_tmp_variable(c, op))
                            c.add_code('mov ah, 9')
                        else:
                            load_integer(c, op)
                    else:
                        raise ValueError(f'Regex should not have allowed {format_type}')

                    # Call the interruption to print the argument
                    c.add_code(f'int 21h')

                # Argument formatted, print the next part of the string
                define_and_print(c, substrings[i])
        else:
            # No arguments at all, a define and load will do
            define_and_print(c, string)

    # All done, restore the original dx/ax values
    c.add_code('pop dx',
               'pop ax')

printf_statement = Statement(
    #          A string    (formatted)?
    r'printf  ("[\s\S]+") (?:, (CSINM))?|printf  (INM)',
    #                                    Or a single inmediate value

    printf
)
