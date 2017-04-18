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
    """Helper assign with support for assigning 8 bits to 16
        and vice versa, as well as assigning multiple values
        at once"""
    if dst == src:
        return

    dst = get_csv(dst)
    src = get_csv(src)
    if len(dst) != len(src):
        raise ValueError('The amount of values to assign do not match')

    # Single assignment with support for mixed sizes (8 and 16)
    if len(dst) == 1:
        dst = c.apply_constants(dst[0])
        src = c.apply_constants(src[0])

        # Sanity check: destination cannot be an inmediate value
        if parseint(dst) is not None:
            raise ValueError(f'Cannot assign {src} to the inmediate value {dst}')

        # Determine the variables size and location before everything else
        if is_register(dst):
            dst_size = register_size(dst)
            dst_memo = False
        else:
            var = c.variables.get(dst, None)
            if var is None:
                raise ValueError(f'Cannot assign to the unknown variable "{dst}"')
            dst_size = var.size
            dst_memo = True

        # Before determining the size of the source register, check if it is
        # an inmediate value, in which case we only need to make sure that
        # the value is inside the bounds of the destination size
        src_value = parseint(src)
        if src_value is not None:
            minimum = -(2 ** (dst_size - 1))
            maximum = 2 ** dst_size
            if not minimum <= src_value < maximum:
                raise ValueError(f'{src_value} is too big to fit in "{dst}"')

            # It's an okay inmediate value, simply assign it and early exit
            c.add_code(f'mov {dst}, {src_value}')
            return

        # If we're here, it has to be either a register or a variable
        if is_register(src):
            src_size = register_size(src)
            src_memo = False
        else:
            var = c.variables.get(src, None)
            if var is None:
                raise ValueError(f'Cannot assign to the unknown variable "{src}"')
            src_size = var.size
            src_memo = True

        # Special case where both are memory, we need to use a temporary
        # register ('ax' for instance); recursive calls to helperassign()
        # will then take care of the cases where assigning memory + 'ax'
        if dst_memo and src_memo:
            # # # [Case memory to memory]
            # TODO This will have strange results when size dst > size src,
            #      since no masking will be performed on 'ax'
            c.add_code('push ax')
            helperassign(c, 'ax', src)
            helperassign(c, dst, 'ax')
            c.add_code('pop ax')
            return

        # Now that we know the size, and that not both are memory,
        # we can get our hands dirty
        if dst_size == src_size:
            # # # [Case same size]
            # Both sizes are the same, we can directly move the values
            # This should be the only move out there, if other moves
            # are required below they should recursively call helperassign()
            # to optimize this line away if 'dst' and 'src' are the same
            c.add_code(f'mov {dst}, {src}')

        elif dst_size < src_size:
            # The destination is smaller, we have to ignore the high part
            if src_memo or src[-1] != 'x':
                # # # [Case large memory/register to small register]
                # The source is memory, then the destination is a register
                #
                # We need an auxiliary register because we don't want to
                # touch the other part (either of r'[HL]'), and we can't
                # pop a masked value not to lose the rest
                #
                # This is also the case when the source is not memory, but
                # the register doesn't support accessing r'[HL]'
                #
                # Use either 'dx' or 'ax' as auxiliar register (arbitrary
                # as long as it doesn't match the one we want to move to)
                aux = 'dx' if dst[0] == 'a' else 'ax'
                c.add_code(f'push {aux}')
                helperassign(c, aux, src)
                helperassign(c, dst, f'{aux[0]}l')
                c.add_code(f'pop {aux}')
            else:
                # # # [Case large register to small register/memory]
                # We know that we have acces to the low part since it was
                # checked above, otherwise we would have needed that
                # auxiliary to be able to pick only the low part
                helperassign(c, dst, f'{src[0]}l')

        else:
            # The destination is larger, we need to mask the high part.
            # The only case where this is possible is on r'[ABCD][HL]',
            # so we already know that we have access to the 'X' version
            # unless the source is memory
            if src_memo:
                # # # [Case small memory to large register]
                # Check if the register supports accessing to the r'[HL]'
                # Otherwise we need to use a temporary register such as 'ax'
                if dst[-1] == 'x':
                    c.add_code(f'xor {dst[0]}h, {dst[0]}h')
                    helperassign(c, f'{dst[0]}l', src)
                else:
                    c.add_code(f'push ax')
                    c.add_code(f'xor ah, ah')
                    helperassign(c, 'al', src)
                    helperassign(c, dst, 'ax')
                    c.add_code(f'pop ax')
            elif dst_memo:
                # # # [Case small register to large memory]
                # All the 8 bit registers support accessing to 'X', so we
                # can just mask away the high part, move it and restore
                c.add_code(f'push {src[0]}x')

                # We might need to move the high to the low part before masking
                if src[-1] == 'h':
                    helperassign(c, f'{src[0]}l', f'{src[0]}h')
                c.add_code(f'xor {src[0]}h, {src[0]}h')

                helperassign(c, dst, f'{src[0]}x')
                c.add_code(f'pop {src[0]}x')
            else:
                # # # [Case small register to large register]
                if src[-1] == 'l':
                    # We're using the low part, we can directly copy
                    # and then mask the high part with AND or XOR
                    helperassign(c, dst, f'{src[0]}x')
                    if dst[-1] == 'x':
                        c.add_code(f'xor {dst[0]}h, {dst[0]}h')
                    else:
                        c.add_code(f'and {dst}, 0xff')
                else:
                    # We want to assign the src = YH, but it's 8-bits
                    if dst[-1] == 'x':
                        # Destination supports 8-bits access so we can
                        # directly move those and mask away the high part
                        helperassign(c, f'{dst[0]}l', src)
                        c.add_code(f'xor {dst[0]}h, {dst[0]}h')
                    else:
                        # No support to move the 8-bits directly, we need
                        # to save the value, move it, mask it, and move it
                        c.add_code(f'push {src[0]}x')
                        helperassign(c, f'{src[0]}l', src)
                        c.add_code(f'xor {src}, {src}')
                        helperassign(c, dst, f'{src[0]}x')
                        c.add_code(f'pop {src[0]}x')

        # Single assignment done, early exit
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
            # TODO Pushed values should also store their size,
            #      so we know whether we need another intermediate step
            c.add_code(f'pop {dstv}')
            pushed.pop()
        else:
            helperassign(c, dstv, srcv)


def parseint(value):
    """Tries parsing an integer value, returns None on failure"""
    if not value or not value.strip():
        return None

    value = value.strip()
    try:
        if value[0] == "'" and value[-1] == "'":
            return ord(value[1])

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


def get_csv(values):
    """If 'values' is not a list already, converts the values
        to a list of values, comma separated
    """
    if isinstance(values, list):
        return values

    if values and values.strip():
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


def register_size(name):
    """Returns the size of the register, or 16 if it's not a register"""
    return 8 if name[1] in 'hl' else 16
