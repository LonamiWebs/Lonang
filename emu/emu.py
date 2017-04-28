#!/usr/bin/python3.6

import os
import sys
import struct
import shutil
from datetime import datetime

from instructions import instructions, get_ins_params
from machine import Machine
from parser import parsevalues, stripcomments


# keyword -> size in bits
keyword_size = {
    'db': 8,
    'dw': 16
}

# size in bits -> struct pack mode
size_structpack = {
    8: '<b',
    16: '<h'
}


def clear():
    """Clears the screen"""
    rows, cols = shutil.get_terminal_size((80, 25))
    string = ' ' * cols
    for _ in range(rows):
        print(string)


def getstart(line, swith):
    """If 'line' starts with 'swith', returns
       'line' with the starting part stripped
    """
    if line.lower().startswith(swith):
        return line[len(swith):].strip()


def getend(line, ewith):
    """If 'line' ends with 'ewith', returns
       'line' with the ending part stripped
    """
    if line.lower().endswith(ewith):
        return line[:-len(ewith)].strip()


def getlabel(line):
    """Gets the label for 'line', or returns
       None if it's not a label/proc
    """
    proc = getend(line, ' proc')
    if proc is not None:
        return proc

    label = getend(line, ':')
    if label is not None:
        return label


def shouldignore(line):
    """Returns True if 'line' can be safely
       ignored when executing code
    """
    return getlabel(line) is not None or \
           getend(line, 'endp') is not None or \
           getend(line, 'ends') is not None or \
           getend(line, 'segment') is not None






if len(sys.argv) != 2 or not os.path.isfile(sys.argv[1]):
    print('err: the file to run must be passed as a parameter')
    quit()

filename = sys.argv[1]
if not os.path.isfile(filename):
    print(f'err: {filename} not found')
    quit()


machine = Machine()





# The code will be all the lines, so we can use a label index
# (when it appears on the lines) to jump to that line of code
def load_lines(filename):
    lines = []
    with open(filename) as f:
        for line in f:
            line = stripcomments(line)
            if line:
                includes = getstart(line, 'include ')
                if includes:
                    included_name = includes.strip('"')
                    lines.extend(load_lines(included_name))
                else:
                    lines.append(line)
    # All lines and recursively included files loaded
    return lines

lines = load_lines(filename)

# Before anything else, we need to replace the macros on the source
macros = {}
inline_macros = {}

expanded = []
current_macro = None
for line in lines:
    if not current_macro:
        # No macro, this line may define one (single line or not)
        # TODO Support for non-caps, non-surrounding spaces with regex
        if ' EQU ' in line:
            name, value = [s.strip() for s in line.split(' EQU ')]
            inline_macros[name] = value
            continue

        current_macro = getend(line, 'macro')
        if current_macro:
            # This line defined one, so set it
            macros[current_macro] = []
        else:
            # No definition, treat this line as code unless it calls a macro
            if line in macros:
                expanded.extend(macros[line])
            else:
                # TODO Word bounds
                for find, replacement in inline_macros.items():
                    line = line.replace(find, replacement)
                expanded.append(line)

        # Do nothing else on a possible macro header
        continue

    if getend(line, 'endm') is not None:
        # We had a macro, so clear it since it's over
        current_macro = None
        continue

    if current_macro:
        # We had a macro and didn't reach its end, so add code
        # TODO Word bounds, don't copy paste
        for find, replacement in inline_macros.items():
            line = line.replace(find, replacement)
        macros[current_macro].append(line)

# Our new lines are the expanded ones
lines = expanded

current_segment = None
for i, line in enumerate(lines):
    # First we determine if it's a label
    label = getlabel(line)
    if label is not None:
        machine.labels[label] = i
        continue

    # Then we go on and analyze if it's a segment
    if not current_segment:
        current_segment = getend(line, ' segment')
        continue

    if getend(line, 'ends') is not None:
        current_segment = None
        continue

    if current_segment == 'data':
        # If the line starts with any of the keywords, then it has no name
        # TODO Not only use ' ', allow any whitespace
        #      (but don't use default '.split()' because it collapses '  ')
        parts = line.split(' ')
        if any(getstart(line, kw) is not None for kw in keyword_size):
            size = keyword_size[parts[0].lower()]
            values = parsevalues(' '.join(parts[1:]), size)
        else:
            name = parts[0]
            size = keyword_size[parts[1].lower()]
            values = parsevalues(' '.join(parts[2:]), size)
            machine.tag_memory(name, size)

        # Got the values, extend the memory
        machine.add_to_memory(values)
    else:
        pass



# Now find the label on which we should start to run the code
start = None
for line in reversed(lines):
    if line.startswith('end '):
        start = line[len('end '):].strip()
        break

if start is None:
    print('err: end not found')
    quit()

if start not in machine.labels:
    print('err: start label not found')
    quit()


# We have a valid label, so we can start executing code
clear()
machine['ip'] = machine.labels[start]
while True:
    line = lines[machine['ip']]

    if not shouldignore(line):
        ins, params = get_ins_params(line)
        method = instructions.get(ins)
        if method is None:
            print(f'err: instruction {ins} not implemented')
            quit()
        method(machine, params)
        # TODO Maybe 'machine.run()' would be more appropriate
        # TODO Machine could open a server on localhost so it can be
        #      controlled (i.e. breakpoints etc)

        #at = str(machine['ip'] + 1).rjust(4)
        #print(f'[{at} {ins.upper().rjust(6)}]; modifications: {last_sets}')

    machine['ip'] += 1
    if machine['ip'] >= len(lines):
        print('err: machine did not halt')
        quit()
