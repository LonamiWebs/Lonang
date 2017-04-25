from .statement import Statement
from utils import helperassign
from variables import TmpVariables
from operands import Operand


def divide(c, m):
    """Division statement. For instance:
        al /= 4
    """
    dst = Operand(c, m.group(1))
    src = Operand(c, m.group(2))


    if src.value == 0:
        raise ValueError('Cannot divide by 0')


    if src.value and abs(src.value) == 1:
        # One optimization: do nothing or negate
        if src.value < 0:
            c.add_code(f'neg {dst}')
        return


    if src.value is not None:
        # Bit shift optimization: second product is a small multiple of 2
        # http://zsmith.co/intel_m.html#mul or
        # http://zsmith.co/intel_n.html#neg and http://zsmith.co/intel_s.html#sal
        if dst.is_reg or dst.size == 8:
            limit = 80
        else:
            limit = 150

        if dst.is_reg:
            if src.value < 0:
                cost = 3 + 8 + 4 * (-src.value)
            else:
                cost = 8 + 4 * src.value

        if dst.is_mem:
            if src.value < 0:
                cost = 16 + 20 + 4 * (-src.value)
            else:
                cost = 20 + 4 * src.value

        # Now we know our limit, beyond which multiplication is easier
        # and the cost per shift, so we know which values we can use
        if cost < limit:
            # The cost of negating and shifting is less, so we'll do that
            amount = limit // cost
            powers = [2**i for i in range(1, amount + 1)]
            if abs(src.value) in powers:
                # We have a power of two, so perform we can use bit shift
                if src.value < 0:
                    c.add_code(f'neg {dst}')
                    src.value = -src.value

                count = int(src.value ** 0.5)
                c.add_code(f'sar {dst}, {count}')
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

        # Move the result, 'ax', to wherever it should be
        helperassign(c, dst, 'ax')

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

        # Move the result, 'al', to wherever it should be
        helperassign(c, dst, 'al')

        # Restore the used registers
        tmps.restore_all()


divide_statement = Statement(
    r'(VAR) /= (INM)',
    divide
)
