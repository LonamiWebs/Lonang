#!/usr/bin/python3.6

import re

source = \
'''

ax = 5
bx = 84
ax += bx

if bx == 84 { @primerIf
    ax = 7
}

repeat 10 with cx { @primerLoop
    
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


# Global 'if' IDs
ifid = 0

# Pending if jump labels
pending_labels = []

# Compare To Opposite jump Instruction
ctoi = {
    '<': 'jge',
    '>': 'jle',
    '<=': 'jg',
    '>=': 'jl',
    '!=': 'je',
    '==': 'jne'
}


# Used to determine the statement
rassign = re.compile(r'(\w+)\s*=\s*([\w\d]+)')
radd = re.compile(r'(\w+)\s*\+=\s*([\w\d]+)')
rif = re.compile(r'if\s+(\w+)\s*([<>=!]+)\s*([\w\d]+)\s*{\s*(?:@(\w+))?')
rendif = re.compile(r'}')


regexes = [rassign, radd, rif, rendif]

# Action(s) to be appended on successful match
def rassign_geti(m):
    return f'mov {m.group(1)}, {m.group(2)}'


def radd_geti(m):
    return f'mov {m.group(1)}, {m.group(2)}'


def rif_geti(m):
    if m.group(4):
        label = m.group(4)
    else:
        label = 'if' + ifid
        ifid += 1
    
    pending_labels.append(label)
    return [
        f'cmp {m.group(1)}, {m.group(3)}',
        f'{ctoi[m.group(2)]} {label}'
    ]


def rendif_geti(m):
    return f'{pending_labels.pop()}:'


getinstructions = [rassign_geti, radd_geti, rif_geti, rendif_geti]



# Combine both so we can iterate over them
regex_getis = list(zip(regexes, getinstructions))


def parse(source):
    compiled = []
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
                result = geti(m)
                if isinstance(result, str):
                    compiled.append(result)
                elif isinstance(result, list):
                    compiled.extend(result)
                break
        
        if not ok:
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




















