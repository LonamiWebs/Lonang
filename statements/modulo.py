from .statement import Statement
from utils import helperassign
from variables import TmpVariables
from operands import Operand


def is_power_of_2(n):
    """Returns true if 'n' is a power of 2"""
    # Example of powers of 2, in binary:
    #   1000, 1000000, 10, 1, …
    #
    # Example of non-powers of 2, in binary:
    #   1010, 1000001, 11, …
    #
    # So as soon as we find that the first bit is 1, and
    # the number is greater than 1, then it's not a power
    while n > 1:
        if n & 1 == 1:
            return False
        n >>= 1
    return True


def modulo(c, m):
    """Modulo statement. For instance:
        al %= 6
    """
    dst = Operand(c, m.group(1))
    src = Operand(c, m.group(2))


    if src.value == 0:
        raise ValueError('Cannot perform modulo 0')


    if src.value < 0:
        raise ValueError('Negative modulo not implemented')


    if src.value is not None and is_power_of_2(src.value):
        # AND optimization: modulo is a power of 2
        # We only need to mask with 111… until its power.
        # For instance:
        #   1000 (8) - 1 = 111 (7)
        #
        # So n % 8, e.g., 100101, is as simple as masking with 111 -> 101
        mask = src.value - 1
        c.add_code(f'and {dst}, {mask}')
        return


    # We're likely going to need to save some temporary variables
    # No 'push' or 'pop' are used because 'ah /= 3', for instance, destroys 'al'
    # 'al' itself can be pushed to the stack, but a temporary variable can hold
    tmps = TmpVariables(c)

    # In division, the dividend is divided by the divisor to get a quotient
    # dividend \ divisor
    #            quotient
    large_divide = max(dst.size, src.size) > 8

    if large_divide:
        # TODO Division and modulo are pretty similar
        #      except for the last part, assigning the result
        #      \-> Reuse code
        #
        # 16-bits mode, so we use 'ax' as the dividend
        dividend = 'ax'

        # The second factor cannot be an inmediate value
        # Neither AX/DX or variants, because those are used
        # Neither 8 bits, because 16 bits mode is required
        if src.code[0] in 'ad' or src.size != 16 or src.value is not None:
            # Either we use a register, which we would need to save/restore,
            # or we use directly a memory variable, which is just easier
            divisor = tmps.create_tmp('divisor', size=16)
        else:
            divisor = src.code

        # Determine which registers we need to save
        saves = []
        # If the destination is DH or DL, we need to save the opposite part
        # If the destination is not DX, we need to save the whole register
        if dst[0] == 'd':
            if dst[-1] == 'h':
                saves.append('dl')
            elif dst[-1] == 'l':
                saves.append('dh')
            elif dst[-1] != 'x':
                saves.append('dx')
        else:
            saves.append('dx')

        # If the destination is AH or AL, we need to save the opposite part
        # If the destination is not AX, we need to save the whole register
        if dst[0] == 'a':
            if dst[-1] == 'h':
                saves.append('al')
            elif dst[-1] == 'l':
                saves.append('ah')
            elif dst[-1] != 'x':
                saves.append('ax')
        else:
            saves.append('ax')

        # Save the used registers
        tmps.save_all(saves)

        # Load the dividend and divisor into their correct location
        helperassign(c, [dividend, divisor], [dst, src])

        # Perform the division
        c.add_code([
            f'xor dx, dx',
            f'div {divisor}'
        ])

        # Move the result, 'dx', to wherever it should be
        helperassign(c, dst, 'dx')

        # Restore the used registers
        tmps.restore_all()

    else:
        # 8-bits mode, so we use 'al' as the dividend
        dividend = 'al'

        # The second factor cannot be an inmediate value
        # Neither AX/AH because those are used
        # Neither 16 bits, because 8 bits mode is required
        if src.code[0] in 'a' or src.size != 8 or src.value is not None:
            # Either we use a register, which we would need to save/restore,
            # or we use directly a memory variable, which is just easier
            divisor = tmps.create_tmp('divisor', size=8)
        else:
            divisor = src.code

        # If the destination is AH or AL, we need to save the opposite part
        # If the destination is not AX, we need to save the whole register
        if dst[0] == 'a':
            if dst[-1] == 'h':
                tmps.save('al')
            elif dst[-1] == 'l':
                tmps.save('ah')
            elif dst[-1] != 'x':
                tmps.save('ax')
        else:
            tmps.save('ax')

        # Load the dividend and divisor into their correct location
        helperassign(c, [dividend, divisor], [dst, src])

        # Perform the division
        c.add_code([
            f'xor ah, ah',
            f'div {divisor}'
        ])

        # Move the result, 'ah', to wherever it should be
        helperassign(c, dst, 'ah')

        # Restore the used registers
        tmps.restore_all()


modulo_statement = Statement(
    r'(VAR) %= (INM)',
    modulo
)
