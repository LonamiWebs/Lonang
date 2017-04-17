# Compare To jump Instruction
cti = {
    '<': 'jl',
    '>': 'jg',
    '<=': 'jle',
    '>=': 'jge',
    '!=': 'jne',
    '==': 'je'
}

# Compare To Opposite jump Instruction
ctoi = {
    '<': 'jge',
    '>': 'jle',
    '<=': 'jg',
    '>=': 'jl',
    '!=': 'je',
    '==': 'jne'
}


def helperassign(dst, src):
    """Helper assign with support for assigning 8 bits to 16"""
    # TODO Add support for actually assigning CL/CH to CX (i.e. XOR the rest)
    if dst == src:
        return None

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


def get_csv(values):
    """If 'values' is not a list already, converts the values
        to a list of values, comma separated
    """
    if isinstance(values, list):
        return values

    values = values.strip()
    if values:
        return [v.strip() for v in values.split(',')]
    else:
        return []


def is_register(name):
    """Returns True if the given 'name' is a register"""
    if len(name) != 2:
        return False

    if name[0] in 'abcd' and name[1] in 'xhl':
        return True

    return name in ('si', 'di', 'cs', 'ds', 'ss', 'sp', 'bp', 'es')
