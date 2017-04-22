from .statement import Statement
from utils import cti, ctoi


def while_(c, m):
    """While control flow statement. For instance:
        while bx < 4 {
            ; code
        }

        To force at least one iteration
        while dx > 7 or once {
            ; code
        }
    """
    label = c.get_uid(m.group(5))
    labelstart = label + '_s'
    labelend = label + '_e'

    if m.group(4) is None:
        # 'or once' is not present, we might not need to enter the loop
        c.add_code([
            f'cmp {m.group(1)}, {m.group(3)}',
            f'{ctoi[m.group(2)]} {labelend}'
        ])
    c.add_code(f'{labelstart}:')

    # Reenter the loop if condition is met
    c.add_pending_code([
        f'cmp {m.group(1)}, {m.group(3)}',
        f'{cti[m.group(2)]} {labelstart}',

        f'{labelend}:'
    ])


while_statement = Statement(
    r'while  (VAR) ([<>=!]+) (INM)  (or once)? {',
    while_
)
