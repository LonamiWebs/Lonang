import struct


def stripcomments(line):
    """Strips the comments from 'line'"""
    if ';' not in line:
        return line.strip()

    result = []
    in_char = False
    in_string = False
    for c in line:
        if c == "'" and not in_string:
            in_char = not in_char

        elif c == '"' and not in_char:
            in_string = not in_string

        elif c == ';' and not in_char and not in_string:
            break

        result.append(c)

    return ''.join(result).strip()


def splitvalues(line):
    """Splits the comma separated values on 'line'
       with support for strings"""
    if ',' not in line:
        return [line.strip()]

    result = []
    current = []
    in_char = False
    in_string = False
    for c in line:
        if c == "'" and not in_string:
            in_char = not in_char

        elif c == '"' and not in_char:
            in_string = not in_string

        elif c == ',' and not in_char and not in_string:
            # We found a comma and we're not parsing a string or character
            # So append the currently parsed string, if any, and clear it
            current = ''.join(current).strip()
            if current:
                result.append(current)
            current = []
            # Don't add this ',' character to the current string afterwards
            continue

        current.append(c)

    current = ''.join(current).strip()
    if current:
        result.append(current)

    return result


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


def unpack_value(packed, size):
    # Determine the pack type TODO How do we support negative values?
    if size == 8:
        pt = '<B'
    elif size == 16:
        pt = '<H'
    else:
        print(f'err: invalid size for unpacking a value')
        quit()

    return struct.unpack(pt, bytes(packed))[0]


# TODO Copy-paste from operands.py (except for the isinstance part)
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


def parsevalues(value, size):
    """Converts a given value, such a string or
       a vector, into a vector of byte values.

       'size' must be either 8 or 16
    """
    result = []
    values = splitvalues(stripcomments(value))
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


def parse_memory_addr(m, addr):
    """Parses a memory address, like [bx+si+7]"""
    # Supporting addresses like '[bx][si]' -> bx+si'
    #                            ^ skip ^
    #
    # TODO Can I actually transform the base into something inside parenthesis?
    first = addr.find('[')
    base, addr = addr[:first], addr[first:]
    if base:
        accum = m.get_memory_addr(base)
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
    accum += m[operands[0]]
    adding = True
    for i in range(1, len(operands)):
        multiplier = 1 if operators[i-1] == '+' else -1
        accum += multiplier * m[operands[i]]

    return accum
