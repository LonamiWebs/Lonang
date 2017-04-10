#!/usr/bin/python3.6

import re

source = \
'''

ax = 4
bx = 6
ax += bx

if bx == 6 { @primerIf
    ax = 7
}

bx = 0
repeat 10 with cx { @primerLoop
    if ax < 10 {
        bx += 1
    }

    ax += 1
}



'''

# Specification:
#   After the instructions, comments can be written,
#   although it's recommended to mark their start with
#   something like '; comment'
#
#   Only one statement per line
#   Conditionals are, for instance:
#     if condition {
#       code
#     } else {
#       code
#     }
#
#   The braces MUST be in the same line.
#   To label a part, use @label at the end
#
#   Loops, for instance:
#     repeat ax with cx {
#       code
#     }
#
#   This makes it explicit that cx will be used although any other can


# Utilities
class strlist(list):
    def add(self, values):
        """Extends or appends the string value(s)"""
        if isinstance(values, str):
            self.append(values)
        elif isinstance(values, list):
            self.extend(values)
        else:
            self.append(str(values))


# Global IDs
globalid = 0
def get_uid(default=None):
    global globalid

    if default:
        return default

    result = f'_uid_{globalid}'
    globalid += 1
    return result


# Pending closing braces, such as if jump labels
closing_braces = []

# Compare To Opposite jump Instruction
ctoi = {
    '<': 'jge',
    '>': 'jle',
    '<=': 'jg',
    '>=': 'jl',
    '!=': 'je',
    '==': 'jne'
}


# Small utility to build more readable regexes
def recompile(string):
    """Used to compile "readable" regexes, with the following changes:
        ' ' (one space) will be replaced with r'\s*'
        '  ' (two spaces) will be replaced with r'\s+'

        '(?:\s*@(\w+))?' will be added to the end to allow @labelname
    """
    sanitized = string.replace('  ', r'\s+').replace(' ', r'\s*')
    sanitized = sanitized + r'(?:\s*@(\w+))?'
    return re.compile(sanitized)


# List of all "'r' + statement" paired with "'r' + statement + '_geti'"
available_statements = [
    'assign', 'add', 'if', 'else', 'repeat'
]

# Used to determine the statement
rassign = recompile(r'(\w+) = ([\w\d]+)')
radd = recompile(r'(\w+) \+= ([\w\d]+)')
rif = recompile(r'if  (\w+) ([<>=!]+) ([\w\d]+) {')
relse = recompile(r'} else {')
rrepeat = recompile(r'repeat  ([\w\d]+)  with  (\w+) {')


def helperassign(dst, src):
    """Helper assign with support for assigning 8 bits to 16"""
    # TODO Add support for actually assigning CL/CH to CX (i.e. XOR the rest)
    return f'mov {dst}, {src}'


def parseint(value):
    """Tries parsing an integer value, returns None on failure"""
    try:
        if value.startswith('0x'):
            return int(value[2:], base=16)

        if value.endswith('h'):
            return int(value[:-1], base=16)

        if value.startswith('0b'):
            return int(value[2:], base=2)

        if value.endswith('b'):
            return int(value[:-1], base=2)

        return int(value)
    except ValueError:
        return None


# Action(s) to be appended on successful match
def rassign_geti(m):
    return helperassign(m.group(1), m.group(2))


def radd_geti(m):
    return f'add {m.group(1)}, {m.group(2)}'


def rif_geti(m):
    label = get_uid(m.group(4))
    closing_braces.append(f'{label}:')
    return [
        f'cmp {m.group(1)}, {m.group(3)}',
        f'{ctoi[m.group(2)]} {label}'
    ]


def relse_geti(m):
    # We consume the if closing brace
    iflabel = closing_braces.pop()[:-1]

    # Build the else label based on the if, unless a name was provided
    if m.group(1):
        elselabel = m.group(1)
    else:
        elselabel = iflabel + '_else'

    # After the else brace closes, ending the met if should skip the else
    closing_braces.append(f'{elselabel}:')

    return [
        # After the if finished, it needs to skip the else end part
        f'jmp {elselabel}',

        # Add the if label back, if this condition was not met
        # on the if jump, then we need to jump here, to the else (if label)
        f'{iflabel}:'
    ]


def rrepeat_geti(m):
    result = []
    label = get_uid(m.group(3))
    labelstart = label + '_s'
    labelend = label + '_e'


    # Initialize our loop counter
    if m.group(1) != m.group(2):
        result.append(helperassign(m.group(2), m.group(1)))

    # Sanity check, if 0 don't enter the loop unless we know it's not 0
    # This won't optimize away the case where the value is 0
    count = parseint(m.group(1))
    if count is None or count <= 0:  # count unknown or zero
        result.append(f'test {m.group(2)}, {m.group(2)}')
        result.append(f'jz {labelend}')

    # Add the start label so we can jump here
    result.append(f'{labelstart}:')

    if m.group(2) == 'cx':
        # We can use 'loop' if using 'cx'
        closing_braces.append([
            f'loop {labelstart}',
            f'{labelend}:'
        ])
    else:
        closing_braces.append([
            f'dec {m.group(2)}',
            f'jnz {labelstart}',
            f'{labelend}:'
        ])

    return result


# Get the regex and their functions and pair them together
g = globals().copy()
regex_getis = [(g[f'r{s}'], g[f'r{s}_geti'])
                for s in available_statements]


def parse(source):
    compiled = strlist()
    for i, line in enumerate(source.split('\n')):
        line = line.strip()
        if not line:
            continue
        
        ok = False
        for regex, geti in regex_getis:
            if not geti:
                continue

            m = regex.search(line)
            if m:
                ok = True
                compiled.add(geti(m))
                break
        
        if ok:
            continue

        # Special case for the closing brace
        if '}' in line:
            try:
                compiled.add(closing_braces.pop())
            except IndexError:
                print(f'ERROR: Non-matching closing brace at line {i+1}')
                return None
        else:
            # Unknown line, error and early exit
            print(f'ERROR: Unknown statement at line {i+1}:\n    {line}')
            return None

    return compiled


compiled = parse(source)

if compiled:
    with open('result.asm', 'w') as f:
        f.write('''data segment

ends

stack segment
    dw   128  dup(0)
ends

code segment
start:
''')
        
        for c in compiled:
            if c[-1] != ':':
                f.write('    ')

            f.write(c)
            f.write('\n')
        
        f.write('''mov ax, 4c00h
int 21h  

ends

end start''')




















