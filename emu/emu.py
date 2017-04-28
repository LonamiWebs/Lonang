#!/usr/bin/python3.6

import os
import sys
import struct
import shutil
from datetime import datetime
from termutils import putch, getch, get_colorama_color
from instructions import instructions, get_ins_params

try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None


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


def normalize(line):
    # TODO strip comments in a nicer way
    semicolon = line.find(';')
    if semicolon != -1:
        line = line[:semicolon]

    return line.strip()


def pack_value(v, size):
    # Determine the pack type
    if size == 8:
        pt = '<b' if v < 0 else '<B'
    elif size == 16:
        pt = '<h' if v < 0 else '<H'
    else:
        print(f'err: invalid size for packing a value')
        quit()

    return struct.pack(pt, v)


# TODO Copy-paste from operands.py
def parseint(value):
    """Tries parsing an integer value, returns None on failure"""
    if isinstance(value, int):
        return value

    if not value or not value.strip():
        return None

    value = value.strip()
    try:
        if value[0] == "'" and value[-1] == "'":
            value = value.strip("'").encode('ascii').decode('unicode_escape')
            if len(value) != 1:
                print('err: character can only be length 1')
                quit()

            return ord(value[0])

        value = value.lower()
        if value.startswith('0x'):
            return int(value[2:], base=16)

        if value[0].isdigit() and value[-1] == 'h':
            return int(value[:-1], base=16)

        if value.startswith('0b'):
            return int(value[2:], base=2)

        if value[0].isdigit() and value[-1] == 'b':
            return int(value[:-1], base=2)

        return int(value)
    except ValueError:
        return None


def twocomp(value, size):
    """Two's complement of 'value'"""
    power = 2**size
    return ((value ^ (power - 1)) + 1) & power - 1


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


def get_values(value, size):
    """Converts a given value, such a string or
       a vector, into a vector of byte values.

       'size' must be either 8 or 16
    """
    # TODO Allow binary values to be specified, do some parseint
    result = []
    values = [normalize(v) for v in value.split(',') if normalize(v)]
    for v in values:
        if 'dup(' in v.lower() and v[-1] == ')':
            count, dup = v.split()
            count = parseint(count)
            dup = dup[len('dup('):-len(')')]
            if dup == '?':
                result.extend(0 for _ in range(count))
            else:
                dup = parseint(dup)
                result.extend(dup for _ in range(count))

        elif v[0] == '"' and v[-1] == '"':
            result.extend(ord(c) for c in v[1:-1])

        elif v[0] == "'" and v[-1] == "'":
            result.append(ord(v[1]))

        elif v == '?':
            result.append(0)

        else:
            if parseint(v) is None:
                print(f'err: could not parse {v} as integer')
                quit()
            result.append(parseint(v))

    return [v for r in result for v in pack_value(r, size)]



if len(sys.argv) != 2 or not os.path.isfile(sys.argv[1]):
    print('err: the file to run must be passed as a parameter')
    quit()

filename = sys.argv[1]
if not os.path.isfile(filename):
    print(f'err: {filename} not found')
    quit()



# TODO We actually don't care about DS value, but we should
memory = []

# name: (index, size)
memory_nameloc = {}


# TODO Infinite stack, not actually what was reserved
stack = []


# Registers and their values
registers = {
    n: 0 for n in 'ax bx cx dx cs ip ss sp bp si di ds es'.split()
}

flags = {
    f: False for f in 'cf zf sf of pf af if df'.split()
}

def isregister(name):
    """Returns True if the given 'name' is a register"""
    name = name.lower()
    if name[-1] in 'xhl':
        return f'{name[0]}x' in registers
    else:
        return name in registers


def access_size(name):
    """Determines the size of the accessed 'name'"""
    if not name:
        return 0

    value = parseint(name)
    if value is not None:
        if value.bit_length() <= 8:
            return 8
        if value.bit_length() <= 16:
            return 16

    if isregister(name):
        name = name.lower()
        if name[-1] in 'hl':
            return 8
        else:
            return 16
    else:
        if '[' in name:
            name = name[:name.index('[')]
            if not name:
                return 8

        _, size = memory_nameloc[name]
        return size

    print(f'err: could not determine size of {name}')
    quit()


def parse_memory_address(addr):
    """Parses a memory address, like [bx+si+7]"""
    # Supporting addresses like '[bx][si]' -> bx+si'
    #                            ^ skip ^
    #
    # TODO can I actually transform the base into something inside parenthesis?
    first = addr.find('[')
    base, addr = addr[:first], addr[first:]
    if base:
        accum = access_get(base)
    else:
        accum = 0

    addr = addr[1:-1] \
                .strip() \
                .replace(']', '') \
                .replace('[', '+')

    # We can't have a starting operator, so prepend 0 if this is the case
    if addr[0] in '+-':
        addr = f'0{addr}'

    # Now determine operators and split on them
    operators = [c for c in addr if c in '+-']
    operands = addr.replace('-', '+').split('+')

    # Now operate
    accum += access_get(operands[0])
    adding = True
    for i in range(1, len(operands)):
        multiplier = 1 if operators[i-1] == '+' else -1
        accum += multiplier * access_get(operands[i])

    return accum


def access_get(name):
    """Accesses to the given name (register, memory...)"""
    if not name:
        return 0

    value = parseint(name)
    if value is not None:
        return value

    if isregister(name):
        name = name.lower()
        if name[-1] == 'h':
            name = f'{name[0]}x'
            return registers[name] >> 8
        elif name[-1] == 'l':
            name = f'{name[0]}x'
            return registers[name] & 0xff
        else:
            return registers[name]
    else:
        if name.lower() == 'data':
            # TODO Not actually returning the location of DS
            return 0

        if '[' in name:
            # TODO Seems like indirect memory access is treated as 8 bits
            idx = parse_memory_address(name)
            take = 1
            pt = size_structpack[8]
        else:
            idx, size = memory_nameloc[name]
            take = size // 8
            pt = size_structpack[size]

        mem = memory[idx:idx+take]
        return struct.unpack(pt, bytes(mem))[0]


last_sets = {}
def access_set(name, value):
    """Accesses to the given name (register, memory...)"""
    # TODO Assert it doesn't access invalid sizes
    if isregister(name):
        if name[-1] == 'h':
            name = f'{name[0]}x'
            registers[name] = (registers[name] & 0x00ff) | (value << 8)
        elif name[-1] == 'l':
            name = f'{name[0]}x'
            registers[name] = (registers[name] & 0xff00) |  value
        else:
            registers[name] = value

        last_sets[name] = registers[name]
    else:
        if '[' in name:
            # TODO Seems like indirect memory access is treated as 8 bits
            idx = parse_memory_address(name)
            size = 8
            take = 1
        else:
            idx, size = memory_nameloc[name]
            take = size // 8

        memory[idx:idx+take] = pack_value(value, size)
        last_sets[name] = value



def alu_operate(op1, op2, operation):
    """Operates with 'operation(op1, op2)' and updates the
       flag registers accordingly (if overflow, zero, etc.)
       returning its result
    """
    # Carry flag (CF)
    # Parity flag (PF)
    # Auxiliary carry flag (AF)
    # Zero flag (ZF)
    # Sign flag (SF)
    # Trap flag (TF)
    # Interrupt flag (IF)
    # Direction flag (DF)
    # Overflow flag (OF)
    size = max(access_size(op1), access_size(op2))
    result = operation(access_get(op1), access_get(op2))

    flags['cf'] = result >= 2**size 
    flags['zf'] = result == 0
    flags['sf'] = (result & (1 << (size - 1))) != 0

    r = result
    flags['pf'] = True
    while r > 0:
        if r & 1 == 1:
            flags['pf'] = not flags['pf']
        r >>= 1

    # A negative result out of positive operands (or vice versa) is an overflow
    comp = twocomp(result, size) if result < 0 else result
    flags['of'] = comp < 0 or comp >= 2**(size-1)

    # TODO flags: AF; TF; IF; DF
    return result


# The code will be all the lines, so we can use a label index
# (when it appears on the lines) to jump to that line of code
def load_lines(filename):
    lines = []
    with open(filename) as f:
        for line in f:
            line = normalize(line)
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

labels = {}
current_segment = None
for i, line in enumerate(lines):
    # First we determine if it's a label
    label = getlabel(line)
    if label is not None:
        labels[label] = i
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
            values = get_values(' '.join(parts[1:]), size)
        else:
            name = parts[0]
            size = keyword_size[parts[1].lower()]
            values = get_values(' '.join(parts[2:]), size)
            memory_nameloc[name] = len(memory), size

        # Got the values, extend the memory
        memory.extend(values)
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

if start not in labels:
    print('err: start label not found')
    quit()


# We have a valid label, so we can start executing code
clear()
registers['ip'] = labels[start]
while True:
    line = lines[registers['ip']]

    if not shouldignore(line):
        ins, params = get_ins_params(line)
        method = instructions.get(ins)
        if method is None:
            print(f'err: instruction {ins} not implemented')
            quit()
        method(None, params)
        # TODO Pass machine state

        #at = str(registers['ip'] + 1).rjust(4)
        #print(f'[{at} {ins.upper().rjust(6)}]; modifications: {last_sets}')
        last_sets.clear()

    registers['ip'] += 1
    if registers['ip'] >= len(lines):
        print('err: machine did not halt')
        quit()
