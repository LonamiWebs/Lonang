from operands import Operand
from variables import TmpVariables


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


def stripcomments(line):
    """Strips the comments from 'line'"""
    if ';' not in line:
        return line.strip()

    p = None
    result = []
    in_char = False
    in_string = False
    for c in line:
        if c == "'" and not in_string and p != '\\':
            in_char = not in_char

        if c == '"' and not in_char and p != '\\':
            in_string = not in_string

        elif c == ';' and not in_char and not in_string:
            break

        result.append(c)
        p = c

    return ''.join(result).strip()


def helperassign(c, dst, src):
    """Helper assign with support for assigning 8 bits to 16
        and vice versa, as well as assigning multiple values
        at once"""
    dst = c.get_operands(dst)
    src = c.get_operands(src)

    if len(dst) != len(src):
        raise ValueError('The amount of values to assign do not match')

    if dst == src:
        return

    # Single assignment with support for mixed sizes (8 and 16)
    if len(dst) == 1:
        helperoperate(c, 'mov', dst[0], src[0])
        return

    # Multiple assignment
    #
    # First we check the case of length 2 (TODO: Could be generalized)
    # in which we have the following situation:
    #   v1, v2 = v3, v1
    #
    # We can swap the order not to lose the required v1 value:
    #   v2, v1 = v1, v3
    #
    # However, there's nothing we can do if v3 were v2
    if len(dst) == 2:
        if dst[0] == src[1] and dst[1] != src[0]:
            # The condition is met, swap the values
            dst[0], dst[1] = dst[1], dst[0]
            src[0], src[1] = src[1], src[0]


    # Now that we have a certain amount of values, copy them as required
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

    # The reason why we don't use push/pop and instead a temporary variable
    # is because we cannot push/pop 8-bit values, and also because we can't
    # use the helperassign() to pop a value with different sizes
    tmps = TmpVariables(c)
    saved = []

    for i in range(len(dst)):
        srcv = src[i]
        dstv = dst[i]

        found = False
        for j in range(i+1, len(dst)):
            if dstv == src[j]:
                found = True
                saved.append(src[j])
                tmps.save(src[j])

        # If the parameter we've saved matches the one being used,
        # use the saved one since it contains the right value
        if saved and saved[-1] == srcv:
            # Restore the last saved temporary variable name
            # to assign its value to the function parameter
            helperassign(c, dstv, tmps[saved[-1]])
            saved.pop()
        else:
            helperassign(c, dstv, srcv)


def helperoperate(c, op, dst, src):
    """Helper operation with support to operate on any value
        (memory or not) of the form 'instruction dst, src'
    """
    if not isinstance(dst, Operand):
        dst = Operand(c, dst)

    if not isinstance(src, Operand):
        src = Operand(c, src)

    # Sanity check: destination cannot be an inmediate value
    if dst.value is not None:
        raise ValueError(f'Cannot {op} "{src.name}" to the inmediate value "{dst.name}"')

    # If the source has an integer value, make sure it fits on destination
    if src.value is not None:
        if src.size > dst.size:
            raise ValueError(f'"{src.name}" is too big to fit in "{dst.name}"')

        # It's an okay inmediate value, simply operate and early exit
        c.add_code(f'{op} {dst}, {src}')
        return

    # Special case where both are memory, we need to use a temporary
    # register ('ax' for instance); recursive calls to helperoperate()
    # will then take care of the cases where operating with memory + 'ax'
    if dst.is_mem and src.is_mem:
        # # # [Case memory to memory]
        # TODO Perhaps we could use a temporary variable instead of the
        #      stack to pick either AL or AX (which is better suited)
        c.add_code('push ax')
        helperassign(c, 'ax', src)
        helperoperate(c, op, dst, 'ax')
        c.add_code('pop ax')
        return

    # Now that we know the size, and that not both are memory,
    # we can get our hands dirty
    if dst.size == src.size:
        # # # [Case same size]
        # Both sizes are the same, we can directly operate (unless 'mov')
        if op != 'mov' or dst != src:
            c.add_code(f'{op} {dst}, {src}')

    elif dst.size < src.size:
        # The destination is smaller, we have to ignore the high part
        if src.is_mem or src.low is None:
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
            helperoperate(c, op, dst, f'{aux[0]}l')
            c.add_code(f'pop {aux}')
        else:
            # # # [Case large register to small register/memory]
            # We know that we have acces to the low part since it was
            # checked above, otherwise we would have needed that
            # auxiliary to be able to pick only the low part
            helperoperate(c, op, dst, src.low)

    else:
        # The destination is larger, we need to mask the high part.
        # The only case where this is possible is on r'[ABCD][HL]',
        # so we already know that we have access to the 'X' version
        # unless the source is memory
        if src.is_mem:
            # # # [Case small memory to large register]
            # Check if the register supports accessing to the r'[HL]'
            # Otherwise we need to use a temporary register such as 'ax'
            if dst.low is None:
                c.add_code(f'push ax')
                c.add_code(f'xor ah, ah')
                helperassign(c, 'al', src)
                helperoperate(c, op, dst, 'ax')
                c.add_code(f'pop ax')
            else:
                c.add_code(f'xor {dst.high}, {dst.high}')
                helperoperate(c, op, dst.low, src)
        elif dst.is_mem:
            # # # [Case small register to large memory]
            # All the 8 bit registers support accessing to 'X', so we
            # can just mask away the high part, move it and restore
            c.add_code(f'push {src.full}')

            # We might need to move the high to the low part before masking
            if src[-1] == 'h':
                helperassign(c, src.low, src.high)
            c.add_code(f'xor {src.high}, {src.high}')

            helperoperate(c, op, dst, src.full)
            c.add_code(f'pop {src.full}')
        else:
            # # # [Case small register to large register]
            if src[-1] == 'l':
                # We're using the low part, we can directly copy
                # and then mask the high part with AND or XOR
                helperoperate(c, op, dst, src.full)
                if dst.high is None:
                    c.add_code(f'and {dst}, 0xff')
                else:
                    c.add_code(f'xor {dst.high}, {dst.high}')
            else:
                # We want to assign the src = YH, but it's 8-bits
                if dst.low is None:
                    # No support to move the 8-bits directly, we need
                    # to save the value, move it, mask it, and move it
                    c.add_code(f'push {src.full}')
                    helperassign(c, src.low, src)
                    c.add_code(f'xor {src}, {src}')
                    helperoperate(c, op, dst, src.full)
                    c.add_code(f'pop {src.full}')
                else:
                    # Destination supports 8-bits access so we can
                    # directly move those and mask away the high part
                    helperoperate(c, op, dst.low, src)
                    c.add_code(f'xor {dst.high}, {dst.high}')
