import re
from common import *
from functions import Function


# Small utility to build more readable regexes
def recompile(string):
    """Used to compile "readable" regexes, with the following changes:
        '^' and '$' will be prepended and appended, respectively

        'VALUE' will be replaced with '[\w\d]+' to match registers/numbers

        ' ' (one space) will be replaced with r'\s*'
        '  ' (two spaces) will be replaced with r'\s+'

        '(?:\s*@(\w+))?' will be added to the end to allow @labelname
    """
    sanitized = string.replace('VALUE', r'[\w\d]+')
    sanitized = sanitized.replace('  ', r'\s+').replace(' ', r'\s*')
    sanitized = sanitized + r'(?:\s*@(\w+))?'
    return re.compile('^' + sanitized + '$')


# List of all "'r' + statement" paired with "'r' + statement + '_geti'"
available_statements = [
    'assign', 'add', 'if', 'else', 'repeat',
    'functiondef', 'functioncall', 'variable'
]


# Regexes used to determine the statement being specified
rassign = recompile(r'(\w+) = (VALUE)')
radd = recompile(r'(\w+) \+= (VALUE)')
rif = recompile(r'if  (\w+) ([<>=!]+) (VALUE) {')
relse = recompile(r'} else {')
rrepeat = recompile(r'repeat  (VALUE)  with  (\w+) {')
rfunctiondef = recompile(r'function (\w+) \(([\w, ]+)\)(?: returns (\w+))? {')
rfunctioncall = recompile(r'(?:(\w+) = )?(\w+)\(([\w, ]+)\)')

rvariable = recompile(r'''(byte|short|string|const)  (\w+) = (.+)''')

# Implementation for the above statements, i.e.,
# action(s) to be appended on successful match
#
# 'c' represents the current Compiler
# 'm' represents the Matched statement

def rassign_geti(c, m):
    """Assignment statement. For instance:
        ax = bx
    """
    c.add_code(helperassign(m.group(1), m.group(2)))


def radd_geti(c, m):
    """Addition statement. For instance:
        dx += cx
    """
    c.add_code(f'add {m.group(1)}, {m.group(2)}')


def rif_geti(c, m):
    """If control flow statement. For instance:
        if ax < 5 {
            ; code
        }
    """
    label = c.get_uid(m.group(4))
    c.add_code(
        f'cmp {m.group(1)}, {m.group(3)}',
        f'{ctoi[m.group(2)]} {label}'
    )
    c.add_pending_code(f'{label}:')


def relse_geti(c, m):
    """Else control flow statement. For instance:
        } else {
            ; code
        }
    """
    # We consume the if closing brace (TODO which should be a closing brace!)
    iflabel = c.pending_code.pop()[:-1]

    # Build the else label based on the if, unless a name was provided
    if m.group(1):
        elselabel = m.group(1)
    else:
        elselabel = iflabel + '_else'

    c.add_code(
        # After the if finished, it needs to skip the else end part
        f'jmp {elselabel}',

        # Add the if label back, if this condition was not met
        # on the if jump, then we need to jump here, to the else (if label)
        f'{iflabel}:'
    )

    # After the else brace closes, ending the met if should skip the else
    c.add_pending_code(f'{elselabel}:')


def rrepeat_geti(c, m):
    """Repeat control flow statement. For instance:
        repeat 10 with cx {
            ; code
        }
    """
    label = c.get_uid(m.group(3))
    labelstart = label + '_s'
    labelend = label + '_e'


    # Initialize our loop counter
    if m.group(1) != m.group(2):
        c.add_code(helperassign(m.group(2), m.group(1)))

    # Sanity check, if 0 don't enter the loop unless we know it's not 0
    # This won't optimize away the case where the value is 0
    count = parseint(m.group(1))
    if count is None or count <= 0:  # count unknown or zero
        c.add_code(f'test {m.group(2)}, {m.group(2)}')
        c.add_code(f'jz {labelend}')

    # Add the start label so we can jump here
    c.add_code(f'{labelstart}:')

    if m.group(2) == 'cx':
        # We can use 'loop' if using 'cx'
        c.add_pending_code([
            f'loop {labelstart}',
            f'{labelend}:'
        ])
    else:
        c.add_pending_code([
            f'dec {m.group(2)}',
            f'jnz {labelstart}',
            f'{labelend}:'
        ])


def rvariable_geti(c, m):
    """Variable or constant definition. For instance:
        byte little = 42
        short big = 1234
        
        const VALUE = 7
    """
    # TODO Support for vectors (SomeString DB 23 DUP(?))
    # TODO Perform more checks to ensure the value is correct
    if m.group(1) == 'byte':
        c.add_variable(f'{m.group(2)} DB {m.group(3)}')

    elif m.group(1) == 'short':
        c.add_variable(f'{m.group(2)} DW {m.group(3)}')

    elif m.group(1) == 'string':
        # Analyze scape sequences and trim the quotes
        ana = m.group(3).strip('"').encode('ascii').decode('unicode_escape')
        quote_open = False
        result = ''

        for analyzed in ana:
            if ord(analyzed) <= 32:
                # Non-printable
                if quote_open:
                    result += '", '
                    quote_open = False
                result += str(ord(analyzed))
                result += ', '
            else:
                # Printable
                if not quote_open:
                    result += '"'
                    quote_open = True
                result += analyzed

        if quote_open:
            result += '"'

        result += ", '$'"
        # Now we have our resulting string encoded properly
        c.add_variable(f'{m.group(2)} DB {result}')

    elif m.group(1) == 'const':
        c.add_constant(m.group(2), m.group(3))


def rfunctiondef_geti(c, m):
    """Function definition. For instance:
        function myMethod(ax) returns dx {
            ; code
        }
    """
    c.begin_function(Function(m))


def rfunctioncall_geti(c, m):
    """Function call. For instance:
        dx = someMethod(8)
    """
    assigned_to = m.group(1)
    name = m.group(2)
    params = Function.get_params(m.group(3))

    # Find the function TODO Maybe as a method from the compiler state
    function = None
    for f in c.functions:
        # The argument count and name must match
        if f.name == name and len(f.params) == len(params):
            # If we don't assign the result, or we do but it's
            # okay because the function returns something
            if assigned_to is None or f.returns is not None:
                # Then assign we've found our function
                function = f
                break

    if function is None:
        raise ValueError(
            f'No function called {name} with {len(params)} argument(s) exists')

    # We have a function, now copy the parameters if required
    for caller_p, func_p in zip(params, function.params):
        if caller_p != func_p:
            # Caller parameter and function parameter differs, we need to move
            c.add_code(helperassign(func_p, caller_p))

    # Parameters are ready, call the function
    c.add_code(f'call {name}')

    # Copy the result back if it differs from where the function stored it
    if assigned_to is not None and function.returns != assigned_to:
        c.add_code(helperassign(assigned_to, function.returns))


# Get the regex and their functions and pair them together
g = globals().copy()
regex_getis = [(g[f'r{s}'], g[f'r{s}_geti'])
                for s in available_statements]
