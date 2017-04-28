from .statement import Statement
from utils import helperassign
from variables import TmpVariables
from operands import Operand
from .divide import perform_divide


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

    perform_divide(c, dst, src,
                   result_in8='ah',
                   result_in16='dx')


modulo_statement = Statement(
    r'(VAR) %= (INM)',
    modulo
)
