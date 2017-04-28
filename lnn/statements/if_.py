from .statement import Statement
from operands import Operand
from utils import ctoi


def if_(c, m):
    """If control flow statement. For instance:
        if ax < 5 {
            ; code
        }

        if cx is even {
            ; code
        }
    """
    a = Operand(c, m.group(1))
    comparision = m.group(2)
    b = Operand(c, m.group(3))

    even_odd = m.group(4)
    label = c.get_uid(m.group(5))

    if even_odd is None:
        c.add_code([
            f'cmp {a}, {b}',
            f'{ctoi[comparision]} {label}'
        ])
    else:
        # If even, then bit is 0, then jump to skip if not zero
        # If  odd, then bit is 1, then jump to skip if zero
        jump = 'jnz' if even_odd == 'even' else 'jz'
        c.add_code([
            f'test {a}, 1',
            f'{jump} {label}'
        ])

    c.add_pending_code(f'{label}:')


if_statement = Statement(
    r'if  (VAR)(?: ([<>]|[<>!=]=) (INM)|  is  (even|odd)) {',
    if_
)
