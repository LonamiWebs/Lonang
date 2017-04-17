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


def helperassign(c, dst, src):
    """Helper assign with support for assigning 8 bits to 16"""
    # TODO Add support for actually assigning CL/CH to CX (i.e. XOR the rest)
    if dst == src:
        return

    dst = get_csv(dst)
    src = get_csv(src)
    if len(dst) != len(src):
        raise ValueError('The amount of values to assign do not match')

    # Quick, most straightforward case
    if len(dst) == 1:
        c.add_code(f'mov {dst[0]}, {src[0]}')
        return

    # Multiple assignment
    # We have a function, now copy the parameters if required
    #
    # If a source value is assigned to a destination value,
    # and this destination value appears later as as a source value,
    # we need to push it to the stack or we'd lose it:
    #
    #   ax, bx = bx, ax
    #       ^    ^
    #        \    \_ we assign 'ax' to this
    #         \
    #          \_ appears later as a source value, but we assigned 'ax' to it!
    #
    # Also append as many times as we find it, for instance:
    #   ax, bx, cx = bx, ax, ax
    #
    # But before doing any of this, let's make sure there's no 'ax = ax'
    for i in reversed(range(len(dst))):
        if dst[i] == src[i]:
            dst.pop(i)
            src.pop(i)

    # And let's also make sure that they appear once as destination
    duplicated = []
    last_value_dict = {}
    for i in range(len(dst)):
        if dst[i] in last_value_dict:
            # We already had found this value, save the previous
            # duplicated destination for later removal
            duplicated.append(last_value_dict[dst[i]])

        # Update the index for this destination
        last_value_dict[dst[i]] = i

    for i in reversed(duplicated):
        # Someone really typed some non-sense like 'ax, ax = ax, bx'
        dst.pop(i)
        src.pop(i)

    pushed = []
    for i in range(len(dst)):
        srcv = src[i]
        dstv = dst[i]

        found = False
        for j in range(i+1, len(dst)):
            if dstv == src[j]:
                found = True
                pushed.append(src[j])
                c.add_code(f'push {src[j]}')

        # If the parameter we've pushed matches the one being used,
        # use the pushed one since it contains the right value
        if pushed and pushed[-1] == srcv:
            # Pop to assign the value to the function parameter
            c.add_code(f'pop {dstv}')
            pushed.pop()
        else:
            c.add_code(f'mov {dstv}, {srcv}')

    # TODO These 'pop's won't be able to push 8 bits, thus neither pop them,
    #      whereas the basic helperassign() would, in theory, support this


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
