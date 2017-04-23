from .statement import Statement
from utils import helperassign
from variables import TmpVariables
from operands import Operand


def multiply(c, m):
    """Multiplication statement. For instance:
        al *= 7
    """
    dst = Operand(c, m.group(1))
    src = Operand(c, m.group(2))


    if src.value == 0:
        # Zero optimization: second product is 0
        if dst.is_mem:
            c.add_code(f'and {dst}, 0')
        else:
            c.add_code(f'xor {dst}, {dst}')
        return


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
            limit = 70
        else:
            limit = 124

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
                c.add_code(f'sal {dst}, {count}')
                return


    # We're likely going to need to save some temporary variables
    # No 'push' or 'pop' are used because 'ah *= 3', for instance, destroys 'al'
    # 'al' itself can be pushed to the stack, but a temporary variable can hold
    tmps = TmpVariables(c)

    # We will define 'dst, src, fa1, fa2' as:
    #   dst *= src
    #   fa1 *= fa2

    large_multiply = max(dst.size, src.size) > 8


    if large_multiply:
        # 16-bits mode, so we use 'ax' as the first factor
        fa1 = 'ax'

        # The second factor cannot be an inmediate value neither 'ax'
        if src.code[0] == 'a' and src.code[-1] in 'xhl' \
                or src.value is not None:
            fa2 = 'dx'
        else:
            fa2 = src.code

        # Determine which registers we need to save
        saves = []

        # al    *= 260
        # ^ dst
        #
        # ax    *= 260
        # ^ used
        #
        # dst ≠ used, used gets saved

        # Special case where we want to use al/ah as destination
        # We're using ax for multiplication, so we can't save the whole
        if dst[0] == 'a' and dst[-1] in 'hl':
            saves.append('al' if dst.code == 'ah' else 'ah')
        elif dst.code != fa1:
            # Save fa1 unless it's the destination
            saves.append(fa1)

        # Save fa2 unless it's the destination
        if dst.code != fa2:
            saves.append(fa2)

        # Save the used registers
        tmps.save_all(saves)

        # Load the factors into their correct location
        helperassign(c, [fa1, fa2], [dst, src])

        # Perform the multiplication
        c.add_code(f'mul {fa2}')

        # Move the result, 'ax', to wherever it should be
        helperassign(c, dst, 'ax')

        # Clear dx unless saved or that's the destination, in which
        # case xor'ing would be useless since overrode on restore
        if dst.code != 'dx' and 'dx' not in saves:
            c.add_code('xor dx, dx')

        # Restore the used registers
        tmps.restore_all()

    else:
        # 8-bits mode, so we use 'al' as the first factor
        fa1 = 'al'

        # The second factor cannot be an inmediate value neither 'al'
        fa2 = src.code if src.value is None and src.code != 'al' else 'ah'

        # Determine which registers we need to save
        saves = []

        # Save fa1 unless it's the destination
        if dst.code != fa1:
            saves.append(fa1)

        # Save fa2 if we moved it (thus it's not the same)
        # unless it's be overrode if it is the destination
        if src.code != fa2 and dst.code != fa2:
            saves.append(fa2)

        # Save the used registers
        tmps.save_all(saves)

        # Load the factors into their correct location
        helperassign(c, [fa1, fa2], [dst, src])

        # Perform the multiplication
        c.add_code(f'mul {fa2}')

        # Move the result, 'al', to wherever it should be
        helperassign(c, dst, 'al')

        # Restore the used registers
        tmps.restore_all()


multiply_statement = Statement(
    r'(VAR) \*= (INM)',
    multiply
)
